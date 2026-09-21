"""第5步：CustomerService 业务逻辑的单元测试。"""

import pytest
from pydantic import ValidationError

from app.service import (
    CustomerService,
    CustomerNotFoundError,
    CustomerAlreadyExistsError,
)
from app.repository import CustomerRepository


@pytest.fixture
def service(tmp_path):
    """每个测试用一个全新的临时数据库，跑完自动删。"""
    db_path = tmp_path / "test.db"
    repo = CustomerRepository(db_path=str(db_path))
    return CustomerService(repository=repo)


class TestCreateCustomer:
    def test_create_success(self, service):
        customer = service.create_customer("1001", "张三", age=25)
        assert customer.customer_id == "1001"
        assert customer.name == "张三"

    def test_duplicate_id_rejected(self, service):
        service.create_customer("1001", "张三")
        with pytest.raises(CustomerAlreadyExistsError):
            service.create_customer("1001", "李四")


class TestGetCustomer:
    def test_get_existing(self, service):
        service.create_customer("1001", "张三")
        customer = service.get_customer("1001")
        assert customer.name == "张三"

    def test_get_not_found(self, service):
        with pytest.raises(CustomerNotFoundError):
            service.get_customer("9999")


class TestUpdateCustomer:
    def test_update_email(self, service):
        service.create_customer("1001", "张三")
        updated = service.update_customer("1001", email="zs@example.com")
        assert updated.email == "zs@example.com"

    def test_update_not_found(self, service):
        with pytest.raises(CustomerNotFoundError):
            service.update_customer("9999", email="x@x.com")

    def test_update_bad_email_rejected(self, service):
        service.create_customer("1001", "张三")
        with pytest.raises(ValidationError):
            service.update_customer("1001", email="这不是邮箱")


class TestDeleteCustomer:
    def test_delete_success(self, service):
        service.create_customer("1001", "张三")
        service.delete_customer("1001")
        with pytest.raises(CustomerNotFoundError):
            service.get_customer("1001")

    def test_delete_not_found(self, service):
        with pytest.raises(CustomerNotFoundError):
            service.delete_customer("9999")


class TestListAndSearch:
    def test_list_all(self, service):
        service.create_customer("1001", "张三")
        service.create_customer("1002", "李四")
        customers = service.list_customers()
        assert len(customers) == 2

    def test_search_by_name(self, service):
        service.create_customer("1001", "张三")
        service.create_customer("1002", "张三")
        results = service.search_customers("张三")
        assert len(results) == 2
