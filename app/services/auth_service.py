from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import Role
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expires_at,
    verify_password,
)
from app.models import AuthSession, Merchant, User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut


def _build_user_out(db: Session, user: User) -> UserOut:
    merchant = db.scalar(select(Merchant).where(Merchant.user_id == user.id))
    return UserOut(
        id=user.id,
        role=user.role,
        login_name=user.login_name,
        display_name=user.display_name,
        phone=user.phone,
        merchant_id=merchant.id if merchant else None,
        store_name=merchant.store_name if merchant else None,
    )


def _create_session(db: Session, user: User) -> tuple[str, datetime]:
    raw_token = generate_session_token()
    expires_at = session_expires_at()
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_session_token(raw_token),
            role=user.role,
            expires_at=expires_at,
        )
    )
    return raw_token, expires_at


def register_user(db: Session, payload: RegisterRequest) -> AuthResponse:
    if payload.role == Role.PLATFORM:
        if not settings.platform_register_invite_code or (
            payload.invite_code != settings.platform_register_invite_code
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="平台邀请码无效")

    existing = db.scalar(
        select(User).where(
            User.role == payload.role.value,
            User.login_name == payload.login_name,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该账号已注册")

    if payload.role == Role.MERCHANT and not payload.store_name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请填写店铺名称")

    user = User(
        role=payload.role.value,
        login_name=payload.login_name.strip(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
        phone=payload.phone,
        status="active",
        last_login_at=datetime.now(),
    )
    db.add(user)
    db.flush()

    if payload.role == Role.MERCHANT:
        db.add(
            Merchant(
                user_id=user.id,
                store_name=payload.store_name.strip(),
                contact_name=payload.display_name.strip(),
                phone=payload.phone,
                status="active",
            )
        )
        db.flush()

    token, expires_at = _create_session(db, user)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=token, expires_at=expires_at, user=_build_user_out(db, user))


def login_user(db: Session, payload: LoginRequest) -> AuthResponse:
    user = db.scalar(
        select(User).where(
            User.role == payload.role.value,
            User.login_name == payload.login_name.strip(),
        )
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    user.last_login_at = datetime.now()
    token, expires_at = _create_session(db, user)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=token, expires_at=expires_at, user=_build_user_out(db, user))


def logout_session(db: Session, auth_session: AuthSession) -> None:
    auth_session.revoked_at = datetime.now()
    db.commit()


def get_user_out(db: Session, user: User) -> UserOut:
    return _build_user_out(db, user)


def cleanup_expired_sessions(db: Session, older_than_days: int = 7) -> None:
    cutoff = datetime.now() - timedelta(days=older_than_days)
    sessions = db.scalars(select(AuthSession).where(AuthSession.expires_at < cutoff)).all()
    for item in sessions:
        db.delete(item)
    db.commit()
