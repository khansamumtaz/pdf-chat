import secrets
from datetime import datetime, timedelta, timezone
from .config import settings
from .security import generate_otp, hash_otp

def issue_otp(db, model, user_id: int) -> str:
    db.query(model).filter(model.user_id == user_id, model.used == False).update({"used": True})
    otp = generate_otp()
    db.add(model(
        user_id=user_id,
        otp_hash=hash_otp(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    ))
    db.commit()
    return otp

def check_otp(db, model, user_id: int, otp: str) -> bool:
    row = (
        db.query(model)
        .filter(model.user_id == user_id, model.used == False)
        .order_by(model.id.desc())
        .first()
    )
    if not row or row.expires_at < datetime.now(timezone.utc):
        return False
    if not secrets.compare_digest(row.otp_hash, hash_otp(otp)):
        return False
    row.used = True
    db.commit()
    return True