"""客户数据的增删改查（第3步：SQLite 持久化）。"""

from datetime import datetime
from typing import Optional

from app.customer import Customer
from app.database import get_connection, init_db


class CustomerRepository:
    """只负责存取数据，不做业务判断（业务判断是第4步 Service 的事）。"""

    def __init__(self, db_path=None) -> None:
        self.db_path = db_path  # ← 存下来
        init_db(db_path)  # ← 传给建表

    @staticmethod
    def _row_to_customer(row) -> Customer:
        """把数据库一行记录转成 Customer 对象。"""
        return Customer(
            customer_id=row["customer_id"],
            name=row["name"],
            age=row["age"],
            phone=row["phone"],
            email=row["email"],
        )

    def create(self, customer: Customer) -> Customer:
        """插入一条客户记录。"""
        now = datetime.now().isoformat(timespec="seconds")
        conn = get_connection(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO customers
                    (customer_id, name, age, phone, email, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (customer.customer_id, customer.name, customer.age,
                 customer.phone, customer.email, now, now),
            )
            conn.commit()
        finally:
            conn.close()
        return customer

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """按 ID 查客户，查不到返回 None。"""
        conn = get_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM customers WHERE customer_id = ?",
                (customer_id,),
            ).fetchone()
            return self._row_to_customer(row) if row else None
        finally:
            conn.close()

    def search_by_name(self, name: str) -> list[Customer]:
        """按姓名查客户（可能同名多个）。"""
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM customers WHERE name = ?",
                (name,),
            ).fetchall()
            return [self._row_to_customer(row) for row in rows]
        finally:
            conn.close()

    def update(self, customer_id: str, fields: dict) -> Optional[Customer]:
        """只更新传入的字段，传了哪些改哪些。客户不存在返回 None。"""
        if not fields:
            return self.get_by_id(customer_id)

        assignments = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [
            datetime.now().isoformat(timespec="seconds"),
            customer_id,
        ]
        conn = get_connection(self.db_path)
        try:
            cur = conn.execute(
                f"UPDATE customers SET {assignments}, updated_at = ? WHERE customer_id = ?",
                values,
            )
            conn.commit()
            if cur.rowcount == 0:
                return None
        finally:
            conn.close()
        return self.get_by_id(customer_id)

    def delete(self, customer_id: str) -> bool:
        """删除客户，删成功返回 True，客户不存在返回 False。"""
        conn = get_connection(self.db_path)
        try:
            cur = conn.execute(
                "DELETE FROM customers WHERE customer_id = ?",
                (customer_id,),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def list_all(self) -> list[Customer]:
        """列出所有客户。"""
        conn = get_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM customers ORDER BY customer_id"
            ).fetchall()
            return [self._row_to_customer(row) for row in rows]
        finally:
            conn.close()
