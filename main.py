import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from pipeline import process_documents

from openpyxl import Workbook

# PDF 출력용
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors


# PDF → 이미지 변환 (PyMuPDF)
def pdf_to_images(pdf_path: Path, dpi: int = 200) -> list[str]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("[오류] pymupdf가 설치되어 있지 않습니다. `pip install pymupdf` 후 다시 시도하세요.")
        sys.exit(1)

    out_dir = Path(tempfile.mkdtemp(prefix="pdf_pages_"))
    image_paths = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            out_path = out_dir / f"{pdf_path.stem}_p{i+1}.png"
            pix.save(out_path.as_posix())
            image_paths.append(out_path.as_posix())
    return image_paths


def collect_inputs(user_path: str) -> list[str]:
    IMG_EXT = {".png", ".jpg", ".jpeg"}
    PDF_EXT = {".pdf"}

    p = Path(user_path)

    if not p.exists():
        print(f"[오류] 입력 경로가 존재하지 않습니다: {user_path}")
        sys.exit(1)

    final_images: list[str] = []

    if p.is_file() and p.suffix.lower() in PDF_EXT:
        final_images.extend(pdf_to_images(p))
    elif p.is_file() and p.suffix.lower() in IMG_EXT:
        final_images.append(p.as_posix())
    elif p.is_dir():
        for f in p.iterdir():
            ext = f.suffix.lower()
            if ext in IMG_EXT:
                final_images.append(f.as_posix())
            elif ext in PDF_EXT:
                final_images.extend(pdf_to_images(f))
    else:
        print("[안내] 처리할 수 있는 PDF나 이미지 파일/폴더가 아닙니다.")
        sys.exit(1)

    if not final_images:
        print("[안내] 입력에서 처리할 파일을 찾지 못했습니다.")
        sys.exit(1)

    return final_images


def save_as_json(results: dict, out_dir: Path, timestamp: str):
    json_path = out_dir / f"analysis_result_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[저장 완료] JSON → {json_path}")


def save_as_excel(results: dict, out_dir: Path, timestamp: str):
    wb = Workbook()

    # 시트1: 조항 분석
    ws1 = wb.active
    ws1.title = "조항 분석"
    ws1.append(["Clause", "Numbers", "Dates", "Risk Score", "Risk Keywords"])
    for c in results.get("clauses", []):
        ws1.append([
            c["clause"],
            ", ".join(c["entities"]["numbers"]),
            ", ".join(c["entities"]["dates"]),
            c["risk"]["score"],
            ", ".join(c["risk"]["matched_keywords"]),
        ])

    # 시트2: 임베딩 매칭
    ws2 = wb.create_sheet("임베딩 매칭")
    ws2.append(["Clause", "Matched Text", "Similarity"])
    for m in results.get("embedding_match", []):
        clause_text = m["clause"]
        for match in m["matches"]:
            ws2.append([
                clause_text,
                match["text"],
                match["similarity"],
            ])

    excel_path = out_dir / f"analysis_result_{timestamp}.xlsx"
    wb.save(excel_path)
    print(f"[저장 완료] Excel → {excel_path}")


def save_as_pdf(results: dict, out_dir: Path, timestamp: str):
    pdf_path = out_dir / f"analysis_result_{timestamp}.pdf"

    # 한글 지원 폰트 등록
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

    # 기본 스타일
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "HYSMyeongJo-Medium"
    styles["Title"].fontName = "HYSMyeongJo-Medium"
    styles["Heading2"].fontName = "HYSMyeongJo-Medium"

    # 표 안 전용 스타일
    from reportlab.lib.styles import ParagraphStyle
    korean_style = ParagraphStyle(
        name="Korean",
        fontName="HYSMyeongJo-Medium",
        fontSize=9,
        leading=12
    )

    # PDF 문서 생성
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    elements = []

    # 제목
    elements.append(Paragraph("분석 리포트", styles["Title"]))
    elements.append(Spacer(1, 20))

    # --- 조항 분석 표 ---
    elements.append(Paragraph("1. 조항 분석", styles["Heading2"]))

    table_data = [[
        Paragraph("Clause", korean_style),
        Paragraph("Risk Score", korean_style),
        Paragraph("Risk Keywords", korean_style)
    ]]

    for c in results.get("clauses", []):
        table_data.append([
            Paragraph(c["clause"], korean_style),
            Paragraph(str(c["risk"]["score"]), korean_style),
            Paragraph(", ".join(c["risk"]["matched_keywords"]), korean_style)
        ])

    table = Table(table_data, colWidths=[300, 60, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- 임베딩 매칭 표 ---
    elements.append(Paragraph("2. 유사 임베딩 매칭", styles["Heading2"]))

    match_data = [[
        Paragraph("Clause", korean_style),
        Paragraph("Matched Text", korean_style),
        Paragraph("Similarity", korean_style)
    ]]

    for m in results.get("embedding_match", []):
        for match in m["matches"]:
            match_data.append([
                Paragraph(m["clause"], korean_style),
                Paragraph(match["text"], korean_style),
                Paragraph(f"{match['similarity']:.3f}", korean_style)
            ])

    match_table = Table(match_data, colWidths=[300, 120, 80])
    match_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(match_table)

    # PDF 저장
    doc.build(elements)
    print(f"[저장 완료] PDF → {pdf_path}")



def main():
    # .env 로드
    load_dotenv()
    api_url = os.getenv("API_URL")
    secret_key = os.getenv("SECRET_KEY")

    if not api_url or not secret_key:
        print("[오류] API_URL 또는 SECRET_KEY가 .env에 없습니다.")
        sys.exit(1)

    # 사용자 입력
    user_path = input("분석할 이미지 폴더 또는 단일 PDF/이미지 파일 경로를 입력하세요: ").strip()
    user_path = user_path.strip('"').strip("'")

    image_files = collect_inputs(user_path)

    # 출력 형식 선택
    output_format = input("저장 형식을 선택하세요 (json / excel / pdf / 모두): ").strip().lower()

    risk_keywords = ["위약금", "손해배상", "강제", "의무"]
    example_db = ["예시 조항1", "예시 조항2"]

    results = process_documents(image_files, api_url, secret_key, risk_keywords, example_db)

    # 콘솔 출력
    print("=== 최종 분석 결과 ===")
    for r in results["clauses"]:
        print(r)

    print("\n=== 유사 임베딩 매칭 결과 ===")
    for m in results["embedding_match"]:
        print(m)

    # 결과 저장 디렉토리 (고정)
    out_dir = Path("D:/25-2ocr2/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_format == "json":
        save_as_json(results, out_dir, timestamp)
    elif output_format == "excel":
        save_as_excel(results, out_dir, timestamp)
    elif output_format == "pdf":
        save_as_pdf(results, out_dir, timestamp)
    elif output_format == "모두":
        save_as_json(results, out_dir, timestamp)
        save_as_excel(results, out_dir, timestamp)
        save_as_pdf(results, out_dir, timestamp)
    else:
        print("[안내] 알 수 없는 형식입니다. 아무 것도 저장하지 않았습니다.")


if __name__ == "__main__":
    main()
