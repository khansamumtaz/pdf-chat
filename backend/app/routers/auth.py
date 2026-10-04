import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, EmailOTP
from ..schemas import SignupIn, VerifyOTPIn, EmailIn, LoginIn, TokenOut, MessageOut
from ..security import hash_password, verify_password, create_access_token
from ..otp_service import issue_otp, check_otp
from ..email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger("uvicorn.error")

def _send(user: User, otp: str):
    try:
        send_otp_email(user.email, otp, "verify your email")
    except Exception:
        logger.exception("SMTP failed")
        raise HTTPException(502, "Could not send OTP email. Check SMTP settings.")

@router.post("/signup", response_model=MessageOut, status_code=201)
def signup(data: SignupIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if user and user.is_verified:
        raise HTTPException(400, "Email already registered")
    if not user:
        user = User(name=data.name, email=email, password_hash=hash_password(data.password))
        db.add(user)
    else:
        user.name = data.name
        user.password_hash = hash_password(data.password)
    db.commit()
    db.refresh(user)
    _send(user, issue_otp(db, EmailOTP, user.id))
    return {"message": "Account created. Check your email for the OTP."}

@router.post("/verify-email", response_model=MessageOut)
def verify_email(data: VerifyOTPIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not check_otp(db, EmailOTP, user.id, data.otp):
        raise HTTPException(400, "Invalid or expired OTP")
    user.is_verified = True
    db.commit()
    return {"message": "Email verified. You can now log in."}

@router.post("/resend-otp", response_model=MessageOut)
def resend_otp(data: EmailIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if user and not user.is_verified:
        _send(user, issue_otp(db, EmailOTP, user.id))
    return {"message": "If the account exists, a new OTP has been sent."}

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_verified:
        raise HTTPException(403, "Email not verified. Please verify your OTP first.")
    return {"access_token": create_access_token(user.id)}