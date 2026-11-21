from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, require_roles
from app.core.constants import Role
from app.db.session import get_db
from app.models import Merchant
from app.schemas.conversation import MerchantOptionOut
from app.services.serializers import serialize_merchant

router = APIRouter(prefix="/platform/merchants", tags=["平台-商家"])
platform_only = require_roles(Role.PLATFORM)


@router.get("", response_model=list[MerchantOptionOut])
def search_merchants(
    keyword: str | None = Query(default=None),
    _auth: AuthContext = Depends(platform_only),
    db: Session = Depends(get_db),
) -> list[MerchantOptionOut]:
    stmt = select(Merchant).where(Merchant.status == "active").order_by(Merchant.id)
    if keyword:
        term = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                Merchant.store_name.ilike(term),
                Merchant.contact_name.ilike(term),
                Merchant.phone.ilike(term),
            )
        )
    merchants = db.scalars(stmt.limit(50)).all()
    return [serialize_merchant(merchant) for merchant in merchants]
