"""
Authentication service.

Responsibilities:
  - Password hashing / verification (bcrypt)
  - JWT access token creation / decoding
  - OTP generation, storage, verification
  - Email delivery via SMTP (OTP codes)

All functions are stateless and importable — no class needed here.
"""

import random
import string
import smtplib
import logging
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db import User, OTPCode, _utcnow
from app.core.exceptions import AuthError, InvalidOTPError

logger = logging.getLogger(__name__)
settings = get_settings()


# --------------------------------------------------------------------------- #
#  Password                                                                     #
# --------------------------------------------------------------------------- #

def hash_password(plain: str) -> str:
    """Return bcrypt hash of a plaintext password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plaintext matches the bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# --------------------------------------------------------------------------- #
#  JWT                                                                          #
# --------------------------------------------------------------------------- #

def create_access_token(user_id: str) -> str:
    """Create a signed JWT containing the user_id as 'sub'."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str:
    """
    Decode a JWT and return the user_id (sub).
    Raises AuthError on invalid or expired token.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise AuthError("Token payload missing subject.")
        return user_id
    except JWTError as e:
        raise AuthError(f"Invalid or expired token: {e}")


# --------------------------------------------------------------------------- #
#  OTP                                                                          #
# --------------------------------------------------------------------------- #

def _generate_otp() -> str:
    """Generate a 6-digit numeric OTP."""
    return "".join(random.choices(string.digits, k=6))


def create_otp(user_id: str, purpose: str, db: Session) -> str:
    """
    Invalidate any existing OTPs for this user+purpose,
    create a new one, persist it, and return the code.
    """
    # Invalidate old OTPs for same purpose
    db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.purpose == purpose,
        OTPCode.used == False,
    ).update({"used": True})

    code = _generate_otp()
    expires_at = _utcnow() + timedelta(minutes=settings.otp_expire_minutes)

    otp_record = OTPCode(
        user_id=user_id,
        code=code,
        purpose=purpose,
        expires_at=expires_at,
    )
    db.add(otp_record)
    db.commit()
    return code


def verify_otp(user_id: str, code: str, purpose: str, db: Session) -> None:
    """
    Verify an OTP code. Marks it used if valid.
    Raises InvalidOTPError if wrong, expired, or already used.
    """
    otp = db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.code == code,
        OTPCode.purpose == purpose,
        OTPCode.used == False,
    ).first()

    if otp is None:
        raise InvalidOTPError("OTP is invalid or has already been used.")

    if _utcnow() >= otp.expires_at:
        otp.used = True
        db.commit()
        raise InvalidOTPError(
            f"OTP has expired. Please request a new one. "
            f"(Expired at {otp.expires_at.isoformat()})"
        )

    otp.used = True
    db.commit()


# --------------------------------------------------------------------------- #
#  Email                                                                        #
# --------------------------------------------------------------------------- #

def send_otp_email(to_email: str, code: str, purpose: str) -> None:
    """
    Send an OTP code via SMTP.
    If SMTP credentials are not configured, logs the OTP instead (dev mode).
    """
    if not settings.smtp_user or not settings.smtp_password:
        # Dev mode — no email configured, just log the code
        logger.warning(
            f"[DEV MODE] No SMTP configured. OTP for {to_email} "
            f"({purpose}): {code}"
        )
        return

    subject_map = {
        "verify_email": "Your Resume Analyzer — Email Verification Code",
        "reset_password": "Your Resume Analyzer — Password Reset Code",
    }
    subject = subject_map.get(purpose, "Your OTP Code")

    body_html = f"""
    <html><body>
    <h2>Your verification code</h2>
    <p>Use this code to complete your request:</p>
    <h1 style="letter-spacing:8px;font-size:36px;color:#2563eb;">{code}</h1>
    <p>This code expires in <b>{settings.otp_expire_minutes} minutes</b>.</p>
    <p>If you didn't request this, ignore this email.</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from or settings.smtp_user, to_email, msg.as_string())
        logger.info(f"OTP email sent to {to_email} (purpose={purpose})")
    except Exception as e:
        # Don't crash the request if email fails — log and continue
        # In production you'd want a queue / retry here
        logger.error(f"Failed to send OTP email to {to_email}: {e}")
