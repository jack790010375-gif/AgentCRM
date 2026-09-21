"""Agent 工具层（第6步）：把 Service 函数包装成大模型可调用的工具。"""

from langchain_core.tools import tool
from pydantic import ValidationError

from app.service import CustomerService, ServiceError

# 全局共享一个 Service 实例
service = CustomerService()


@tool
def create_customer(
    customer_id: str,
    name: str,
    age: int = None,
    phone: str = None,
    email: str = None,
) -> str:
    """创建一个新客户。客户ID必须是纯数字，姓名不能为空，年龄0~150。

    Args:
        customer_id: 客户唯一编号，必须是纯数字
        name: 客户姓名，不能为空
        age: 客户年龄，0~150，可选
        phone: 手机号，11位大陆手机号，可选
        email: 邮箱地址，可选
    """
    try:
        customer = service.create_customer(customer_id, name, age, phone, email)
        return f"客户{customer.customer_id}（{customer.name}）创建成功"
    except (ServiceError, ValidationError) as e:
        return f"创建失败：{e}"


@tool
def get_customer(customer_id: str) -> str:
    """根据客户ID查询客户信息。

    Args:
        customer_id: 客户唯一编号
    """
    try:
        customer = service.get_customer(customer_id)
        return str(customer)
    except ServiceError as e:
        return f"查询失败：{e}"


@tool
def search_customers(name: str) -> str:
    """根据客户姓名搜索客户，可能返回多个同名客户。

    Args:
        name: 客户姓名
    """
    customers = service.search_customers(name)
    if not customers:
        return f"没有找到姓名为{name}的客户"
    return "\n".join(str(c) for c in customers)


@tool
def update_customer(
    customer_id: str,
    email: str = None,
    phone: str = None,
    age: int = None,
) -> str:
    """修改客户信息，只修改传入的字段，不传的字段保持不变。

    Args:
        customer_id: 客户唯一编号
        email: 新的邮箱地址，可选
        phone: 新的手机号，可选
        age: 新的年龄，0~150，可选
    """
    try:
        fields = {}
        if email is not None:
            fields["email"] = email
        if phone is not None:
            fields["phone"] = phone
        if age is not None:
            fields["age"] = age
        customer = service.update_customer(customer_id, **fields)
        return f"客户{customer_id}修改成功：{customer}"
    except (ServiceError, ValidationError) as e:
        return f"修改失败：{e}"


@tool
def delete_customer(customer_id: str) -> str:
    """删除客户。

    Args:
        customer_id: 客户唯一编号
    """
    try:
        service.delete_customer(customer_id)
        return f"客户{customer_id}已删除"
    except ServiceError as e:
        return f"删除失败：{e}"


@tool
def list_customers() -> str:
    """列出所有客户。"""
    customers = service.list_customers()
    if not customers:
        return "当前没有客户"
    return "\n".join(str(c) for c in customers)


# 工具列表，后面 LangGraph 会用到
all_tools = [
    create_customer,
    get_customer,
    search_customers,
    update_customer,
    delete_customer,
    list_customers,
]
