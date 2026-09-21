"""客户管理业务逻辑层（第4步）。

所有业务规则集中在这里：ID 重复、客户不存在、空字段不更新等。
Repository 只管存取，Service 管规则。
"""

from app.customer import Customer
from app.repository import CustomerRepository


class ServiceError(Exception):
    """业务错误基类，所有自定义错误都继承它。"""


class CustomerAlreadyExistsError(ServiceError):
    """客户 ID 已存在。"""


class CustomerNotFoundError(ServiceError):
    """客户不存在。"""


class CustomerService:
    """客户管理业务逻辑。"""

    def __init__(self, repository: CustomerRepository | None = None) -> None:
        self.repo = repository or CustomerRepository()

    def create_customer(
        self,
        customer_id: str,
        name: str,
        age: int | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> Customer:
        """创建客户：先查重复 → 再校验 → 最后保存。"""
        # 规则1：ID 不能重复
        if self.repo.get_by_id(customer_id) is not None:
            raise CustomerAlreadyExistsError(f"客户ID {customer_id} 已存在")

        # 规则2：Pydantic 自动校验（不合法会抛 ValidationError）
        customer = Customer(
            customer_id=customer_id,
            name=name,
            age=age,
            phone=phone,
            email=email,
        )

        # 规则3：保存
        self.repo.create(customer)
        return customer

    def get_customer(self, customer_id: str) -> Customer:
        """按 ID 查客户，不存在就报错。"""
        customer = self.repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(f"客户ID {customer_id} 不存在")
        return customer

    def search_customers(self, name: str) -> list[Customer]:
        """按姓名查客户，可能返回多个同名客户。"""
        return self.repo.search_by_name(name)

    def update_customer(self, customer_id: str, **fields) -> Customer:
        """修改客户：必须存在、空字段不改、新值要重新校验。"""
        # 规则1：客户必须存在
        old = self.repo.get_by_id(customer_id)
        if old is None:
            raise CustomerNotFoundError(f"客户ID {customer_id} 不存在")

        # 规则2：过滤掉 None（用户没传的字段不改）
        clean_fields = {k: v for k, v in fields.items() if v is not None}
        if not clean_fields:
            return old

        # 规则3：把旧值和新值合并，用 Customer 重新校验
        # （直接改数据库会绕过 Pydantic，所以必须先过一遍校验）
        merged = old.model_dump()
        merged.update(clean_fields)
        Customer(**merged)  # 不合法会直接抛 ValidationError

        self.repo.update(customer_id, clean_fields)
        return self.get_customer(customer_id)

    def delete_customer(self, customer_id: str) -> None:
        """删除客户，不存在就报错。"""
        if not self.repo.delete(customer_id):
            raise CustomerNotFoundError(f"客户ID {customer_id} 不存在")

    def list_customers(self) -> list[Customer]:
        """列出所有客户。"""
        return self.repo.list_all()
