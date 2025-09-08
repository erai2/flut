from datetime import date

def split_tags(s: str):
    if not s: return []
    return [t.strip() for t in s.split(",") if t.strip()]

def get_ganji_day(target_date: date) -> str:
    """
    지정된 날짜의 일진(육십갑자)을 계산합니다.
    기준일: 2000년 1월 1일 (경진일)
    """
    start_date = date(2000, 1, 1)
    delta = (target_date - start_date).days

    cheon_gan = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
    ji_ji = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

    # 2000-01-01은 경진일 (천간 인덱스 6, 지지 인덱스 4)
    gan_idx = (6 + delta) % 10
    ji_idx = (4 + delta) % 12

    return f"{cheon_gan[gan_idx]}{ji_ji[ji_idx]}"
