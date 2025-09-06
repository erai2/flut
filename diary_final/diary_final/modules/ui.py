
# modules/ui.py
# 역할: 공통 UI 컴포넌트/렌더링(카드, 목록, 타임라인, 토스트 등)

import streamlit as st
from html import escape

def ok(msg: str): st.success(msg)
def warn(msg: str): st.warning(msg)

def render_diary_snippets(items):
    if not items:
        st.caption("최근 일기가 없습니다.")
        return
    for it in items:
        text = (it.get("text") or "")[:140]
        st.markdown(f"**{it.get('date')}** · {it.get('mood','')}  \n{escape(text)}…")

def render_memos(items):
    if not items:
        st.caption("등록된 메모가 없습니다.")
        return
    for m in items:
        pin = "🔖 " if m.get("pinned") else ""
        tags = m.get("tags") or ""
        st.markdown(f"- **{pin}{escape(m.get('text',''))}**  \n<small>{escape(tags)}</small> · <small>{escape(m.get('created_at',''))}</small>", unsafe_allow_html=True)

def render_todos(items, on_toggle, on_delete):
    if not items:
        st.caption("오늘 할 일이 없습니다.")
        return
    for t in items:
        c1, c2, c3 = st.columns([0.08, 0.72, 0.20])
        with c1:
            new = st.checkbox(" ", value=bool(t["done"]), key=f"done_{t['id']}")
            if new != bool(t["done"]):
                on_toggle(t["id"], new)
        with c2:
            due = t.get("due") or "--:--"
            st.markdown(f"**{escape(t.get('title',''))}**  \n<small>{due} · {t.get('priority','보통')}</small>", unsafe_allow_html=True)
        with c3:
            if st.button("🗑️ 삭제", key=f"del_{t['id']}"):
                on_delete(t["id"])

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
                st.markdown(f"- **{r.get('text','')}**  \n<small>{r.get('tags','')}</small> · <small>{r.get('created_at','')}</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"- **[{r['d']}] {r.get('title','')}**  \n<small>{r.get('due') or '--:--'} · {r.get('priority','보통')} · {'완료' if r.get('done') else '미완료'}</small>", unsafe_allow_html=True)
