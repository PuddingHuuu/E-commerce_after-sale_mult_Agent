from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.core.constants import Role
from app.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    role: Role
    login_name: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    store_name: str | None = Field(default=None, max_length=120)
    invite_code: str | None = None

    @model_validator(mode="after")
    def validate_role_fields(self) -> "RegisterRequest":
        if self.role == Role.MERCHANT and not self.store_name:
            raise ValueError("商家注册必须填写店铺名称")
        return self


class LoginRequest(BaseModel):
    role: Role
    login_name: str
    password: str
    remember: bool = True


class UserOut(ORMModel):
    id: int
    role: str
    login_name: str
    display_name: str
    phone: str | None = None
    merchant_id: int | None = None
    store_name: str | None = None


class AuthResponse(BaseModel):
    token: str
    expires_at: datetime
    user: UserOut


class MeResponse(BaseModel):
    user: UserOut


class LogoutResponse(BaseModel):
    message: str = "已退出登录"
