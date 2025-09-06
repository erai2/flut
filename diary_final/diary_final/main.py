
# main.py
# 역할: Streamlit 메인 앱. "오늘/타임라인/검색/설정" 탭으로 즉시 쓰기/찾기 중심 UX 제공.
# 데이터는 반드시 ./data/app.db (SQLite)에 저장. (오프라인 우선, 내보내기/노션 동기화 제공)

import os
import streamlit as st
from datetime import date, time, datetime, timedelta
from modules import db, ui, utils
from modules.notion_client import NotionSync

st.set_page_config(page_title="오늘 일기·메모·할 일", page_icon="🗒️", layout="wide")

# --- 데이터 디렉토리/DB 준비 ---
os.makedirs("data/exports", exist_ok=True)
conn = db.get_conn("data/app.db")
db.init_schema(conn)
notion = NotionSync()  # .env 없으면 enabled=False

# --- 상단 헤더 ---
st.title("🗒️ 오늘 일기 · 메모 · 할 일")
st.caption("최소 클릭 · 즉시 저장 · 오프라인 우선")

# --- 탭 구성 ---
tab_today, tab_timeline, tab_search, tab_settings = st.tabs(["오늘", "타임라인", "검색", "설정/내보내기"])

# ===== [1] 오늘 =====
with tab_today:
    col1, col2, col3 = st.columns([1.2, 1.0, 1.0], gap="large")
    sel_date = st.date_input("날짜", value=date.today(), format="YYYY-MM-DD")

    # --- (A) 오늘 일기 ---
    with col1:
        st.subheader("📓 오늘 일기", divider="gray")
        existing = db.get_diary_for_date(conn, sel_date)
        diary_text = st.text_area("오늘 있었던 일/감정/배운 점", value=existing.get("text",""), height=220, placeholder="자유롭게 적어보세요")
        mood = st.select_slider("기분", ["😣","😕","😐","🙂","😄"], value=existing.get("mood","🙂") or "🙂")
        tags_str = st.text_input("태그 (쉼표로 구분)", value=",".join(existing.get("tags",[])))
        if st.button("💾 일기 저장", type="primary"):
            db.upsert_diary(conn, sel_date, diary_text, mood, utils.split_tags(tags_str))
            ui.ok("일기 저장 완료!")

        with st.expander("📚 오늘/최근 보기", expanded=False):
            ui.render_diary_snippets(db.get_diary_recent(conn, center=sel_date, limit=7))

    # --- (B) 빠른 메모 ---
    with col2:
        st.subheader("🗂️ 빠른 메모", divider="gray")
        memo_text = st.text_area("떠오르는 생각을 바로 기록", height=140, placeholder="예: 아이디어, 링크, 회의키워드 …")
        memo_tags = st.text_input("메모 태그", placeholder="예: 아이디어, 업무")
        pinned = st.checkbox("🔖 상단 고정", value=False)
        colm1, colm2 = st.columns([0.6, 0.4])
        with colm1:
            if st.button("➕ 메모 추가"):
                if memo_text.strip():
                    db.add_memo(conn, memo_text.strip(), utils.split_tags(memo_tags), pinned)
                    ui.ok("메모 추가 완료")
                    st.experimental_rerun()
                else:
                    ui.warn("메모 내용을 입력하세요.")
        with colm2:
            if st.button("🧹 최근 10개 보기 새로고침"):
                st.experimental_rerun()

        st.markdown("##### 📒 최신 메모")
        ui.render_memos(db.list_memos(conn, limit=10))

    # --- (C) 오늘 할 일 ---
    with col3:
        st.subheader("✅ 오늘 할 일", divider="gray")
        c1, c2 = st.columns([0.65, 0.35])
        with c1:
            todo_title = st.text_input("할 일", placeholder="예: 장보기, 보고서 초안")
        with c2:
            due_t = st.time_input("시간", value=time(18,0), step=300)

        priority = st.selectbox("우선순위", ["보통","높음","긴급"], index=0)
        if st.button("➕ 할 일 추가"):
            if todo_title.strip():
                db.add_todo(conn, todo_title.strip(), sel_date, due_t, priority)
                ui.ok("할 일 추가 완료")
                st.experimental_rerun()
            else:
                ui.warn("할 일 제목을 입력하세요.")

        st.markdown("##### 🧾 목록 (미완료→긴급→시간순 정렬)")
        todos = db.list_todos_for_date(conn, sel_date)
        ui.render_todos(todos, on_toggle=lambda tid, val: db.set_todo_done(conn, tid, val),
                        on_delete=lambda tid: (db.delete_todo(conn, tid), st.experimental_rerun()))

    st.divider()
    # (선택) 노션 동기화 퀵 액션
    if notion.enabled:
        coln1, coln2 = st.columns([0.5,0.5])
        with coln1:
            if st.button("🔗 오늘 일기/메모 → Notion"):
                d_count = notion.sync_diary(db.get_diary_for_date(conn, sel_date), sel_date)
                m_count = notion.sync_memos(db.list_memos(conn, limit=50))
                ui.ok(f"일기 {d_count}건, 메모 {m_count}건 동기화")
        with coln2:
            if st.button("🔗 오늘 할 일 → Notion"):
                t_count = notion.sync_todos(db.list_todos_for_date(conn, sel_date))
                ui.ok(f"할 일 {t_count}건 동기화")
    else:
        st.info("`.env`에 노션 토큰/DB_ID를 채우면 동기화 버튼이 활성화됩니다.")

# ===== [2] 타임라인 =====
with tab_timeline:
    st.subheader("🗓️ 타임라인(주/월)", divider="gray")
    today = date.today()
    range_mode = st.radio("범위", ["최근 7일","이번 달"], horizontal=True, index=0)
    if range_mode == "최근 7일":
        start_d = today - timedelta(days=6)
        end_d = today
    else:
        start_d = today.replace(day=1)
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_d = next_month - timedelta(days=1)

    diaries = db.get_diaries_between(conn, start_d, end_d)
    todos_sum = db.get_todo_summary_between(conn, start_d, end_d)
    ui.render_timeline(diaries, todos_sum)

# ===== [3] 검색 =====
with tab_search:
    st.subheader("🔎 통합 검색", divider="gray")
    q = st.text_input("키워드", placeholder="내용/태그/기분/우선순위…")
    colf1, colf2, colf3, colf4 = st.columns(4)
    with colf1:
        f_kind = st.multiselect("종류", ["일기","메모","할 일"], default=["일기","메모","할 일"])
    with colf2:
        f_mood = st.multiselect("기분(일기)", ["😣","😕","😐","🙂","😄"], default=[])
    with colf3:
        f_done = st.selectbox("완료여부(할 일)", ["전체","미완료","완료"], index=0)
    with colf4:
        f_tag = st.text_input("태그 필터", placeholder="쉼표로 다중")

    if st.button("검색 실행", type="primary") or q:
        results = db.search_all(conn, q=q, kinds=f_kind, moods=f_mood, done=f_done, tags=utils.split_tags(f_tag))
        ui.render_search_results(results)
    else:
        st.caption("키워드 또는 필터를 입력해 검색하세요.")

# ===== [4] 설정/내보내기 =====
with tab_settings:
    st.subheader("⚙️ 설정 & 내보내기", divider="gray")
    colx, coly = st.columns([0.5,0.5])
    with colx:
        if st.button("⬇️ 전체 CSV 번들 내보내기"):
            out_paths = db.export_csv_bundle(conn, out_dir="data/exports")
            ui.ok("내보내기 완료")
            for p in out_paths:
                st.write(f"- {p}")
        st.caption("내보낸 파일은 /data/exports 폴더에 저장됩니다.")

    with coly:
        st.write(f"DB 경로: **data/app.db**")
        if st.button("🔧 DB 점검/최적화 (VACUUM)"):
            db.vacuum(conn)
            ui.ok("VACUUM 완료")

st.caption("💡 팁: 메모는 핀(🔖) 고정이 가능하고, 할 일은 미완료/긴급/시간순으로 정렬됩니다.")
