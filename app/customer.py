"""客户数据模型（第2步：用 Pydantic 重新设计）。"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

_PHONE_RE = re.compile(r"1[3-9]\d{9}")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class Customer(BaseModel):
    """客户数据模型，创建实例时自动校验。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    customer_id: str = Field(description="客户唯一编号，必须是数字字符串")
    name: str = Field(description="客户姓名，不能为空")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="客户年龄，0~150")
    phone: Optional[str] = Field(default=None, description="手机号，11位大陆手机号")
    email: Optional[str] = Field(default=None, description="邮箱地址")

    @field_validator("customer_id")
    @classmethod
    def _check_id(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("客户ID必须是数字")
        return value

    @field_validator("name")
    @classmethod
    def _check_name(cls, value: str) -> str:
        if not value:
            raise ValueError("客户姓名不能为空")
        return value

    @field_validator("phone")
    @classmethod
    def _check_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not _PHONE_RE.fullmatch(value):
            raise ValueError("手机号格式不正确")
        return value

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not _EMAIL_RE.fullmatch(value):
            raise ValueError("邮箱格式不正确")
        return value
