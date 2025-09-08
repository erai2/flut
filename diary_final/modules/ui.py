# modules/ui.py
# 역할: 공통 UI 컴포넌트/렌더링(카드, 목록, 타임라인, 토스트 등)

import streamlit as st
import pandas as pd
from html import escape
from datetime import time

def ok(msg: str): st.toast(f"✅ {msg}")
def warn(msg: str): st.toast(f"⚠️ {msg}")

def render_diary_snippets(items):
    if not items:
        st.caption("최근 일기가 없습니다.")
        return
    for it in items:
        text = (it.get("text") or "")[:140]
        st.markdown(f"**{it.get('date')}** · {it.get('mood','')}  \n{escape(text)}…")

def render_memos(items, on_update, on_delete):
    if not items:
        st.caption("등록된 메모가 없습니다.")
        return
    for m in items:
        mid = m['id']
        is_editing = st.session_state.get('editing_memo_id') == mid

        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            pin = "🔖 " if m.get("pinned") else ""
            tags = m.get("tags") or ""
            st.markdown(f"**{pin}{escape(m.get('text',''))}** \n<small>{escape(tags)}</small> · <small>{escape(m.get('created_at',''))}</small>", unsafe_allow_html=True)

        with col2:
            if st.button("수정", key=f"edit_m_{mid}", use_container_width=True):
                st.session_state['editing_memo_id'] = mid
                st.rerun()
        with col3:
            if st.button("삭제", key=f"del_m_{mid}", use_container_width=True):
                on_delete(mid)

        if is_editing:
            with st.expander("메모 수정", expanded=True):
                with st.form(key=f"form_memo_{mid}"):
                    text = st.text_area("내용", value=m['text'])
                    tags = st.text_input("태그", value=m['tags'])
                    pinned = st.checkbox("상단 고정", value=bool(m['pinned']))

                    sf1, sf2 = st.columns(2)
                    with sf1:
                        if st.form_submit_button("💾 저장", type="primary"):
                            on_update(mid, text, tags, pinned)
                    with sf2:
                        if st.form_submit_button("❌ 취소"):
                            st.session_state['editing_memo_id'] = None
                            st.rerun()

def render_todos(items, on_toggle, on_update, on_delete):
    if not items:
        st.caption("오늘 할 일이 없습니다.")
        return
    for t in items:
        tid = t['id']
        is_editing = st.session_state.get('editing_todo_id') == tid

        c1, c2, c3, c4 = st.columns([0.1, 0.6, 0.15, 0.15])
        with c1:
            new_done = st.checkbox(" ", value=bool(t["done"]), key=f"done_{tid}")
            if new_done != bool(t["done"]):
                on_toggle(tid, new_done)
                st.rerun()
        with c2:
            due = t.get("due") or "--:--"
            st.markdown(f"**{escape(t.get('title',''))}** \n<small>{due} · {t.get('priority','보통')}</small>", unsafe_allow_html=True)
        with c3:
            if st.button("수정", key=f"edit_t_{tid}", use_container_width=True):
                st.session_state['editing_todo_id'] = tid
                st.rerun()
        with c4:
            if st.button("삭제", key=f"del_t_{tid}", use_container_width=True):
                on_delete(tid)

        if is_editing:
            with st.expander("할 일 수정", expanded=True):
                with st.form(key=f"form_todo_{tid}"):
                    title = st.text_input("할 일", value=t['title'])
                    current_due = time.fromisoformat(t['due']) if t['due'] else time(18, 0)
                    due = st.time_input("시간", value=current_due)
                    priority = st.selectbox("우선순위", ["보통", "높음", "긴급"], index=["보통", "높음", "긴급"].index(t['priority'] or '보통'))

                    sf1, sf2 = st.columns(2)
                    with sf1:
                        if st.form_submit_button("💾 저장", type="primary"):
                            on_update(tid, title, due, priority)
                    with sf2:
                        if st.form_submit_button("❌ 취소"):
                            st.session_state['editing_todo_id'] = None
                            st.rerun()

def render_timeline(diaries, todos_summary):
    st.markdown("#### 일기 요약")
    if diaries:
        for d in diaries:
            text = (d.get("text") or "")[:120]
            st.markdown(f"- **{d['d']}** · {d.get('mood','')} — {escape(text)}…")
    else:
        st.caption("선택한 범위의 일기가 없습니다.")

    st.markdown("#### 할 일 완료 현황")
    if todos_summary:
        for r in todos_summary:
            st.markdown(f"- **{r['d']}**: {r['done_cnt']}/{r['total_cnt']} 완료")
    else:
        st.caption("선택한 범위의 할 일 기록이 없습니다.")

def render_charts(diaries, todos_summary):
    st.subheader("📊 데이터 시각화", divider="gray")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 😊 기분 변화 추이")
        if diaries:
            mood_map = {"😣": 1, "😕": 2, "😐": 3, "🙂": 4, "😄": 5}
            df_mood = pd.DataFrame(diaries)
            df_mood['mood_val'] = df_mood['mood'].map(mood_map)
            df_mood['d'] = pd.to_datetime(df_mood['d'])
            df_mood = df_mood.set_index('d')
            st.line_chart(df_mood['mood_val'])
        else:
            st.caption("차트를 표시할 일기 데이터가 없습니다.")

    with col2:
        st.markdown("##### 📈 할 일 완료율 (%)")
        if todos_summary:
            df_todos = pd.DataFrame(todos_summary)
            df_todos['rate'] = (df_todos['done_cnt'] / df_todos['total_cnt'] * 100).round(1)
            df_todos['d'] = pd.to_datetime(df_todos['d'])
            df_todos = df_todos.set_index('d')
            st.bar_chart(df_todos['rate'])
        else:
            st.caption("차트를 표시할 할 일 데이터가 없습니다.")

def render_search_results(results):
    st.markdown("### 결과")
    for k in ["일기","메모","할 일"]:
        data = results.get(k,[])
        st.markdown(f"#### {k} ({len(data)}건)")
        if not data:
            st.caption("결과 없음")
            continue
        for r in data:
            if k == "일기":
                st.markdown(f"- **{r['d']}** · {r.get('mood','')} — {(r.get('text') or '')[:120]}…")
            elif k == "메모":
                st.markdown(f"- **{r.get('text','')}** \n<small>{r.get('tags','')}</small> · <small>{r.get('created_at','')}</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"- **[{r['d']}] {r.get('title','')}** \n<small>{r.get('due') or '--:--'} · {r.get('priority','보통')} · {'완료' if r.get('done') else '미완료'}</small>", unsafe_allow_html=True)