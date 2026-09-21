"""第2步：Pydantic Customer 模型的单元测试。"""

import pytest
from pydantic import ValidationError

from app.customer import Customer


class TestCreateCustomer:
    """创建合法客户。"""

    def test_create_valid_customer(self):
        customer = Customer(
            customer_id="1001",
            name="张三",
            age=25,
            phone="13800138000",
            email="zhangsan@example.com",
        )
        assert customer.customer_id == "1001"
        assert customer.name == "张三"
        assert customer.age == 25
        assert customer.phone == "13800138000"
        assert customer.email == "zhangsan@example.com"

    def test_optional_fields_default_to_none(self):
        customer = Customer(customer_id="1001", name="张三")
        assert customer.age is None
        assert customer.phone is None
        assert customer.email is None


class TestRejectInvalidAge:
    """错误年龄被拒绝。"""

    @pytest.mark.parametrize("bad_age", [-1, 151, 200, "abc"])
    def test_reject_invalid_age(self, bad_age):
        with pytest.raises(ValidationError):
            Customer(customer_id="1001", name="张三", age=bad_age)


class TestRejectInvalidPhone:
    """错误手机号被拒绝。"""

    @pytest.mark.parametrize(
        "bad_phone",
        ["123", "1380013800", "138001380001", "23800138000", "abcdefghijk"],
    )
    def test_reject_invalid_phone(self, bad_phone):
        with pytest.raises(ValidationError):
            Customer(customer_id="1001", name="张三", phone=bad_phone)


class TestRejectInvalidEmail:
    """错误邮箱被拒绝。"""

    @pytest.mark.parametrize(
        "bad_email",
        ["abc", "abc@", "@example.com", "abc@example", "abc example.com"],
    )
    def test_reject_invalid_email(self, bad_email):
        with pytest.raises(ValidationError):
            Customer(customer_id="1001", name="张三", email=bad_email)


class TestRejectInvalidCustomerId:
    """客户 ID 必须是数字。"""

    @pytest.mark.parametrize("bad_id", [" ", "abc", "1001a", "12-3", "  "])
    def test_reject_invalid_customer_id(self, bad_id):
        with pytest.raises(ValidationError):
            Customer(customer_id=bad_id, name="张三")


class TestRejectEmptyName:
    """姓名不能为空。"""

    def test_reject_empty_name(self):
        with pytest.raises(ValidationError):
            Customer(customer_id="1001", name="")

    def test_reject_whitespace_only_name(self):
        with pytest.raises(ValidationError):
            Customer(customer_id="1001", name="   ")
