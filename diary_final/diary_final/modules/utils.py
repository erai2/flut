
# modules/utils.py
# 역할: 태그 문자열 ↔ 리스트, 날짜/포맷 보조 유틸

def split_tags(s: str):
    if not s: return []
    return [t.strip() for t in s.split(",") if t.strip()]
