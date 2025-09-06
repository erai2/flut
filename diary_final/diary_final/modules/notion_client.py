
# modules/notion_client.py
# 역할: .env에 NOTION_TOKEN/NOTION_DB_* 세팅 시 동기화 버튼 활성화.
# 실제 업로드 구현은 Notion SDK 연결이 필요하며, 본 클래스는 안전한 스텁 형태입니다.

import os
from typing import Any, Dict, List
from datetime import date
from dotenv import load_dotenv

load_dotenv()

class NotionSync:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN","")
        self.db_todos = os.getenv("NOTION_DB_TODOS","")
        self.db_diary = os.getenv("NOTION_DB_DIARY","")
        self.db_memos = os.getenv("NOTION_DB_MEMOS","")
        self.enabled = all([self.token, self.db_todos, self.db_diary, self.db_memos])

    def sync_diary(self, diary_row: Dict[str,Any], d: date) -> int:
        if not self.enabled or not diary_row: return 0
        # TODO: notion_client.Client 로 pages.create/upsert 구현
        return 1

    def sync_memos(self, memos: List[Dict[str,Any]]) -> int:
        if not self.enabled: return 0
        return len(memos)

    def sync_todos(self, todos: List[Dict[str,Any]]) -> int:
        if not self.enabled: return 0
        return len(todos)
