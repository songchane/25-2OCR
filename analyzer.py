import re

def extract_special_clauses(full_text: str):
    keyword = "특약사항"
    if keyword not in full_text:
        return []

    section = full_text.split(keyword, 1)[1]
    cut_match = re.search(r'(서명|날인)', section)
    if cut_match:
        section = section[:cut_match.start()]
    section = section.strip()

    num_token = re.compile(r'(?P<num>\d(?:\s?\d)*)\s*[\.．]\s*')
    bullet_chars = "•·∙ㆍ‧●○▪■▶"
    dash_chars = "-–—"
    bullet_sep = re.compile(
        rf'(?:(?<=^)|(?<=\s))[\]\)\(\{{\-–—]*\s*([{re.escape(bullet_chars + dash_chars)}])\s+(?=\S)'
    )

    num_matches = list(num_token.finditer(section))
    bullet_matches = list(bullet_sep.finditer(section))

    use_bullet_mode = bool(
        bullet_matches and (not num_matches or bullet_matches[0].start() < num_matches[0].start())
    )

    clauses = []
    if use_bullet_mode:
        marked = bullet_sep.sub('|||', section)
        parts = [p.strip('[](){} .-–—•·∙ㆍ‧●○▪■▶') for p in marked.split('|||') if p.strip()]
        normalized = [re.sub(r'\s+', ' ', p) for p in parts]
        clauses = normalized
    else:
        if not num_matches:
            sentences = re.findall(r'[^\.。!?！？]+[\.。!?！？]', section)
            return [f"{i+1}. {s.strip()}" for i, s in enumerate(sentences)]
        for i, m in enumerate(num_matches):
            start = m.end()
            end = num_matches[i+1].start() if i+1 < len(num_matches) else len(section)
            body = section[start:end].strip()
            if body:
                body = re.sub(r'\s+', ' ', body)
                clauses.append(body)

    return [f"{i+1}. {txt}" for i, txt in enumerate(clauses)]


def tag_entities(text):
    """
    숫자/기간/주체 태깅
    """
    numbers = re.findall(r'\d+', text)
    dates = re.findall(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', text)
    # TODO: 더 정교한 태깅 규칙 추가 가능
    return {"numbers": numbers, "dates": dates}


def match_risk_keywords(text, risk_keywords):
    """
    위험 키워드 매칭 및 간단한 점수 계산
    """
    score = 0
    found = []
    for word in risk_keywords:
        if word in text:
            score += 1
            found.append(word)
    return {"score": score, "matched_keywords": found}