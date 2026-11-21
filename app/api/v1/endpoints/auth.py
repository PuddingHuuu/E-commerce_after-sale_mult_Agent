from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_current_auth
from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutResponse,
    MeResponse,
    RegisterRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return auth_service.register_user(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return auth_service.login_user(db, payload)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    auth: AuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> LogoutResponse:
    auth_service.logout_session(db, auth.session)
    return LogoutResponse()


@router.get("/me", response_model=MeResponse)
def me(
    auth: AuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
) -> MeResponse:
    return MeResponse(user=auth_service.get_user_out(db, auth.user))
