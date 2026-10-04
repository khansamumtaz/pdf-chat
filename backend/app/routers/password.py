import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, PasswordResetOTP
from ..schemas import EmailIn, ResetPasswordIn, MessageOut
from ..security import hash_password
from ..otp_service import issue_otp, check_otp
from ..email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger("uvicorn.error")

@router.post("/forgot-password", response_model=MessageOut)
def forgot_password(data: EmailIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if user and user.is_verified:
        otp = issue_otp(db, PasswordResetOTP, user.id)
        try:
            send_otp_email(user.email, otp, "reset your password")
        except Exception:
            logger.exception("SMTP failed")
            raise HTTPException(502, "Could not send OTP email. Check SMTP settings.")
    return {"message": "If the account exists, a reset OTP has been sent."}

@router.post("/reset-password", response_model=MessageOut)
def reset_password(data: ResetPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not check_otp(db, PasswordResetOTP, user.id, data.otp):
        raise HTTPException(400, "Invalid or expired OTP")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password reset successful. You can now log in."}