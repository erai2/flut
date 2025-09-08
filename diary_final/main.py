# main.py
# 역할: Streamlit 메인 앱. "오늘/타임라인/검색/설정" 탭으로 즉시 쓰기/찾기 중심 UX 제공.
# 데이터는 반드시 ./data/app.db (SQLite)에 저장. (오프라인 우선, 내보내기/노션 동기화 제공)

import os
import calendar
import streamlit as st
from datetime import date, time, datetime, timedelta
from streamlit_option_menu import option_menu

from modules import db, ui, utils
from modules.notion_client import NotionSync

st.set_page_config(page_title="오늘 일기·메모·할 일", page_icon="🗒️", layout="wide")

# --- Session State 초기화 ---
if 'editing_memo_id' not in st.session_state:
    st.session_state['editing_memo_id'] = None
if 'editing_todo_id' not in st.session_state:
    st.session_state['editing_todo_id'] = None
if 'selected_date' not in st.session_state:
    st.session_state['selected_date'] = date.today()

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

# ===== [1] 오늘 (캘린더 추가) =====
with tab_today:
    # --- (상단) 캘린더 UI ---
    cal_col1, cal_col2 = st.columns([0.6, 0.4])
    with cal_col1:
        today = date.today()
        # st.session_state.selected_date 를 기준으로 연/월 표시
        current_view = st.session_state.selected_date
        year, month = current_view.year, current_view.month

        # 월 이동 버튼
        nav1, nav2, nav3, nav4 = st.columns([0.3, 0.3, 0.2, 0.2])
        with nav1:
            if st.button(f"◀ {month-1 if month>1 else 12}월"):
                st.session_state.selected_date = current_view.replace(
                    month=month-1 if month > 1 else 12,
                    year=year if month > 1 else year - 1
                )
                st.rerun()
        with nav2:
            if st.button(f"{month+1 if month<12 else 1}월 ▶"):
                 st.session_state.selected_date = current_view.replace(
                    month=month+1 if month < 12 else 1,
                    year=year if month < 12 else year + 1
                )
                 st.rerun()
        with nav3:
            if st.button("오늘"):
                st.session_state.selected_date = today
                st.rerun()

        # 캘린더 렌더링
        cal_data = calendar.monthcalendar(year, month)
        days_header = ["월", "화", "수", "목", "금", "토", "일"]
        cols = st.columns(7)
        for i, day_name in enumerate(days_header):
            cols[i].text(day_name)

        for week in cal_data:
            cols = st.columns(7)
            for i, day_num in enumerate(week):
                if day_num == 0:
                    continue
                day_date = date(year, month, day_num)
                is_selected = (day_date == st.session_state.selected_date)
                is_today = (day_date == today)
                btn_type = "primary" if is_selected else ("secondary" if is_today else "secondary")

                if cols[i].button(f"{day_num}", key=f"day_{day_num}", type=btn_type, use_container_width=True):
                    st.session_state.selected_date = day_date
                    st.rerun()

    with cal_col2:
        # 선택된 날짜 및 일진 표시
        sel_date = st.session_state.selected_date
        ganji_tag = utils.get_ganji_day(sel_date)
        st.markdown(f"### {sel_date.strftime('%Y년 %m월 %d일')} <span style='font-size: 0.8em; background-color: #eee; padding: 3px 6px; border-radius: 5px;'>{ganji_tag}</span>", unsafe_allow_html=True)
        st.caption("캘린더에서 날짜를 선택하여 해당일의 기록을 보거나 작성하세요.")


    st.divider()
    col1, col2, col3 = st.columns([1.2, 1.0, 1.0], gap="large")

    # --- (A) 오늘 일기 ---
    with col1:
        st.subheader("📓 오늘 일기", divider="gray")
        existing = db.get_diary_for_date(conn, sel_date)
        diary_text = st.text_area("오늘 있었던 일/감정/배운 점", value=existing.get("text",""), height=220, placeholder="자유롭게 적어보세요", key=f"diary_text_{sel_date}")
        mood = st.select_slider("기분", ["😣","😕","😐","🙂","😄"], value=existing.get("mood","🙂") or "🙂", key=f"mood_{sel_date}")
        tags_str = st.text_input("태그 (쉼표로 구분)", value=",".join(existing.get("tags",[])), key=f"tags_{sel_date}")
        if st.button("💾 일기 저장", type="primary"):
            db.upsert_diary(conn, sel_date, diary_text, mood, utils.split_tags(tags_str))
            ui.ok("일기 저장 완료!")
            st.rerun()

        with st.expander("📚 오늘/최근 보기", expanded=False):
            ui.render_diary_snippets(db.get_diary_recent(conn, center=sel_date, limit=7))

    # --- (B) 빠른 메모 ---
    with col2:
        st.subheader("🗂️ 빠른 메모", divider="gray")
        with st.form("new_memo_form"):
            memo_text = st.text_area("떠오르는 생각을 바로 기록", height=140, placeholder="예: 아이디어, 링크, 회의키워드 …")
            memo_tags = st.text_input("메모 태그", placeholder="예: 아이디어, 업무")
            pinned = st.checkbox("🔖 상단 고정", value=False)
            submitted = st.form_submit_button("➕ 메모 추가")
            if submitted:
                if memo_text.strip():
                    db.add_memo(conn, memo_text.strip(), utils.split_tags(memo_tags), pinned)
                    ui.ok("메모 추가 완료")
                    st.rerun()
                else:
                    ui.warn("메모 내용을 입력하세요.")

        st.markdown("##### 📒 최신 메모")
        memos = db.list_memos(conn, limit=10)
        def handle_memo_update(mid, text, tags, pinned):
            db.update_memo(conn, mid, text, utils.split_tags(tags), pinned)
            st.session_state['editing_memo_id'] = None
            ui.ok("메모 수정 완료")
            st.rerun()
        def handle_memo_delete(mid):
            db.delete_memo(conn, mid)
            st.session_state['editing_memo_id'] = None
            ui.ok("메모 삭제 완료")
            st.rerun()
        ui.render_memos(memos, on_update=handle_memo_update, on_delete=handle_memo_delete)

    # --- (C) 오늘 할 일 ---
    with col3:
        st.subheader(f"✅ {sel_date.strftime('%m/%d')} 할 일", divider="gray")
        with st.form("new_todo_form"):
            todo_title = st.text_input("할 일", placeholder="예: 장보기, 보고서 초안")
            c1, c2 = st.columns(2)
            with c1:
                due_t = st.time_input("시간", value=time(18,0), step=300)
            with c2:
                priority = st.selectbox("우선순위", ["보통","높음","긴급"], index=0)
            submitted = st.form_submit_button("➕ 할 일 추가")
            if submitted:
                if todo_title.strip():
                    db.add_todo(conn, todo_title.strip(), sel_date, due_t, priority)
                    ui.ok("할 일 추가 완료")
                    st.rerun()
                else:
                    ui.warn("할 일 제목을 입력하세요.")

        st.markdown("##### 🧾 목록 (미완료→긴급→시간순 정렬)")
        todos = db.list_todos_for_date(conn, sel_date)
        def handle_todo_update(tid, title, due, priority):
            db.update_todo(conn, tid, title, due, priority)
            st.session_state['editing_todo_id'] = None
            ui.ok("할 일 수정 완료")
            st.rerun()
        def handle_todo_delete(tid):
            db.delete_todo(conn, tid)
            st.session_state['editing_todo_id'] = None
            ui.ok("할 일 삭제 완료")
            st.rerun()
        ui.render_todos(todos,
                        on_toggle=lambda tid, val: db.set_todo_done(conn, tid, val),
                        on_update=handle_todo_update,
                        on_delete=handle_todo_delete)

    st.divider()
    if notion.enabled:
        # ... (노션 동기화 부분은 기존과 동일)
        pass

# ... 이하 tab_timeline, tab_search, tab_settings 코드는 기존과 동일합니다 ...
# (이하 생략)
# ===== [2] 타임라인 =====
with tab_timeline:
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

    # 데이터 시각화 렌더링
    ui.render_charts(diaries, todos_sum)
    st.divider()

    # 기존 타임라인 렌더링
    st.subheader("🗓️ 타임라인(주/월)", divider="gray")
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
            st.success("내보내기 완료! 아래 파일들이 생성되었습니다.")
            for p in out_paths:
                st.write(f"- `{p}`")
        st.caption("내보낸 파일은 `data/exports` 폴더에 저장됩니다.")

    with coly:
        st.write(f"DB 경로: **data/app.db**")
        if st.button("🔧 DB 점검/최적화 (VACUUM)"):
            db.vacuum(conn)
            st.success("VACUUM 완료")

st.divider()
st.caption("💡 팁: 메모는 핀(🔖) 고정이 가능하고, 할 일은 미완료/긴급/시간순으로 정렬됩니다.")