"""数据库连接和建表（第3步）。"""

import sqlite3
from pathlib import Path

# 数据库文件放在项目根目录的 data/ 下
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "agentcrm.db"


def get_connection(db_path=None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH   # ← 传了就用传的，没传用默认
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None) -> None:
    """创建 customers 表（如果不存在）。"""
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                age         INTEGER,
                phone       TEXT,
                email       TEXT,
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
