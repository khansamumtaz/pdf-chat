from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User, RevokedToken
from ..schemas import MessageOut

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer = HTTPBearer()

@router.post("/logout", response_model=MessageOut)
def logout(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    jti = payload.get("jti")
    if jti:
        db.add(RevokedToken(jti=jti, expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc)))
        db.commit()
    return {"message": "Logged out."}