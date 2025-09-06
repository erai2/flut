
# modules/db.py
# 역할: SQLite 스키마 및 CRUD. 데이터는 항상 ./data/app.db 에 저장.
# 테이블:
#   diary(id PK, d TEXT ISO, text TEXT, mood TEXT, tags TEXT CSV, saved_at TEXT)
#   memos(id PK, text TEXT, tags TEXT CSV, pinned INTEGER, created_at TEXT)
#   todos(id PK, title TEXT, d TEXT ISO, due TEXT HH:MM, priority TEXT, done INTEGER, created_at TEXT)

import sqlite3, csv, os
from datetime import date, datetime
from typing import List, Dict, Any, Optional

def get_conn(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS diary(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        d TEXT NOT NULL,
        text TEXT,
        mood TEXT,
        tags TEXT,
        saved_at TEXT
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_diary_d ON diary(d)")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        tags TEXT,
        pinned INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memos_created ON memos(created_at)")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS todos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        d TEXT,
        due TEXT,
        priority TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_todos_d ON todos(d)")
    conn.commit()

# ---------- 일기 ----------
def upsert_diary(conn, d: date, text: str, mood: str, tags: List[str]):
    cur = conn.cursor()
    cur.execute("DELETE FROM diary WHERE d=?", (d.isoformat(),))
    cur.execute(
        "INSERT INTO diary(d, text, mood, tags, saved_at) VALUES(?,?,?,?,?)",
        (d.isoformat(), text, mood, ",".join(tags), datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()

def get_diary_for_date(conn, d: date) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM diary WHERE d=?", (d.isoformat(),))
    row = cur.fetchone()
    if not row:
        return {"date": d.isoformat(), "text":"", "mood":"🙂", "tags":[]}
    return {"date": row["d"], "text": row["text"] or "", "mood": row["mood"] or "🙂", "tags": (row["tags"] or "").split(",") if row["tags"] else []}

def get_diary_recent(conn, center: date, limit: int = 7) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM diary ORDER BY d DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    return [{"date": r["d"], "mood": r["mood"], "text": r["text"]} for r in rows]

def get_diaries_between(conn, start_d: date, end_d: date) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM diary WHERE d BETWEEN ? AND ? ORDER BY d ASC", (start_d.isoformat(), end_d.isoformat()))
    return [dict(r) for r in cur.fetchall()]

# ---------- 메모 ----------
def add_memo(conn, text: str, tags: List[str], pinned: bool):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memos(text, tags, pinned, created_at) VALUES(?,?,?,?)",
        (text, ",".join(tags), 1 if pinned else 0, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()

def list_memos(conn, limit: int = 20) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM memos ORDER BY pinned DESC, created_at DESC LIMIT ?", (limit,))
    return [dict(r) for r in cur.fetchall()]

# ---------- 할 일 ----------
def add_todo(conn, title: str, d: date, due, priority: str):
    due_str = due.strftime("%H:%M") if due else None
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos(title, d, due, priority, done, created_at) VALUES(?,?,?,?,0,?)",
        (title, d.isoformat(), due_str, priority, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()

def list_todos_for_date(conn, d: date) -> List[Dict[str, Any]]:
    pri_map = {"긴급":3,"높음":2,"보통":1}
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos WHERE d=?",(d.isoformat(),))
    rows = [dict(r) for r in cur.fetchall()]
    rows.sort(key=lambda t: (t["done"], -(pri_map.get(t["priority"],1)), t["due"] or "99:99"))
    return rows

def set_todo_done(conn, tid: int, val: bool):
    cur = conn.cursor()
    cur.execute("UPDATE todos SET done=? WHERE id=?", (1 if val else 0, tid))
    conn.commit()

def delete_todo(conn, tid: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id=?", (tid,))
    conn.commit()

def get_todo_summary_between(conn, start_d: date, end_d: date) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("""
    SELECT d,
           SUM(CASE WHEN done=1 THEN 1 ELSE 0 END) AS done_cnt,
           COUNT(*) AS total_cnt
    FROM todos
    WHERE d BETWEEN ? AND ?
    GROUP BY d ORDER BY d ASC
    """, (start_d.isoformat(), end_d.isoformat()))
    return [dict(r) for r in cur.fetchall()]

# ---------- 검색 ----------
def search_all(conn, q: str, kinds: List[str], moods: List[str], done: str, tags: List[str]) -> Dict[str, Any]:
    result = {"일기":[], "메모":[], "할 일":[]}
    q_like = f"%{q.strip()}%" if q else None
    tag_like = [t.strip() for t in tags if t.strip()]

    cur = conn.cursor()
    # 일기
    if "일기" in kinds:
        sql = "SELECT * FROM diary WHERE 1=1"
        params: List[Any] = []
        if q_like:
            sql += " AND (text LIKE ? OR tags LIKE ? OR mood LIKE ?)"
            params += [q_like, q_like, q_like]
        if moods:
            sql += f" AND mood IN ({','.join(['?']*len(moods))})"
            params += moods
        for t in tag_like:
            sql += " AND tags LIKE ?"
            params += [f"%{t}%"]
        sql += " ORDER BY d DESC LIMIT 100"
        cur.execute(sql, params)
        result["일기"] = [dict(r) for r in cur.fetchall()]

    # 메모
    if "메모" in kinds:
        sql = "SELECT * FROM memos WHERE 1=1"
        params = []
        if q_like:
            sql += " AND (text LIKE ? OR tags LIKE ?)"
            params += [q_like, q_like]
        for t in tag_like:
            sql += " AND tags LIKE ?"
            params += [f"%{t}%"]
        sql += " ORDER BY pinned DESC, created_at DESC LIMIT 100"
        cur.execute(sql, params)
        result["메모"] = [dict(r) for r in cur.fetchall()]

    # 할 일
    if "할 일" in kinds:
        sql = "SELECT * FROM todos WHERE 1=1"
        params = []
        if q_like:
            sql += " AND (title LIKE ? OR priority LIKE ?)"
            params += [q_like, q_like]
        if done != "전체":
            sql += " AND done=?"
            params += [1 if done=="완료" else 0]
        for t in tag_like:
            sql += " AND title LIKE ?"
            params += [f"%{t}%"]
        sql += " ORDER BY d DESC, done ASC, priority DESC LIMIT 100"
        cur.execute(sql, params)
        result["할 일"] = [dict(r) for r in cur.fetchall()]

    return result

# ---------- 내보내기 ----------
def export_csv_bundle(conn, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = []
    # diary
    p1 = os.path.join(out_dir, f"diary_{ts}.csv")
    with open(p1, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["date","mood","tags","text","saved_at"])
        for r in conn.execute("SELECT d,mood,tags,text,saved_at FROM diary ORDER BY d ASC"):
            w.writerow([r[0], r[1], r[2], r[3], r[4]])
    paths.append(p1)
    # memos
    p2 = os.path.join(out_dir, f"memos_{ts}.csv")
    with open(p2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id","created_at","pinned","tags","text"])
        for r in conn.execute("SELECT id,created_at,pinned,tags,text FROM memos ORDER BY created_at ASC"):
            w.writerow([r[0], r[1], r[2], r[3], r[4]])
    paths.append(p2)
    # todos
    p3 = os.path.join(out_dir, f"todos_{ts}.csv")
    with open(p3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id","date","due","priority","done","title","created_at"])
        for r in conn.execute("SELECT id,d,due,priority,done,title,created_at FROM todos ORDER BY d ASC"):
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])
    paths.append(p3)
    return paths

def vacuum(conn):
    conn.execute("VACUUM")
