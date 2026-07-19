"""
Authentication routes:

  POST /api/auth/signup          — Register with email + password
  POST /api/auth/verify-email    — Verify email with OTP
  POST /api/auth/resend-otp      — Resend OTP (verify or reset)
  POST /api/auth/login           — Login → receive JWT
  POST /api/auth/forgot-password — Send password-reset OTP
  POST /api/auth/reset-password  — Set new password with OTP
  GET  /api/auth/me              — Get current user profile (protected)

Flow:
  signup → OTP sent → verify-email → login → JWT → use protected routes
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.db import get_db, User
from app.models.schemas import (
    SignupRequest, SignupResponse,
    VerifyEmailRequest,
    LoginRequest, TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ResendOTPRequest,
    UserProfileResponse,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_otp,
    verify_otp,
    send_otp_email,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    AuthError,
    UserAlreadyExistsError,
    UserNotVerifiedError,
    InvalidOTPError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


# --------------------------------------------------------------------------- #
#  Signup                                                                       #
# --------------------------------------------------------------------------- #

@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new account.
    Sends a 6-digit OTP to the email — user must verify before logging in.
    """
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise UserAlreadyExistsError(
            f"An account with '{body.email}' already exists."
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create and send OTP
    code = create_otp(user_id=user.id, purpose="verify_email", db=db)
    send_otp_email(to_email=user.email, code=code, purpose="verify_email")

    logger.info(f"New user registered: {user.email}")
    return SignupResponse(
        message="Account created. Check your email for the verification OTP.",
        email=user.email,
    )


# --------------------------------------------------------------------------- #
#  Verify email                                                                 #
# --------------------------------------------------------------------------- #

@router.post("/verify-email", status_code=200)
def verify_email(body: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verify email with the OTP sent at signup.
    After this, the user can log in.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if user is None:
        raise AuthError("No account found with this email.")

    if user.is_verified:
        return {"message": "Email already verified. You can log in."}

    verify_otp(user_id=user.id, code=body.otp, purpose="verify_email", db=db)

    user.is_verified = True
    db.commit()

    logger.info(f"Email verified: {user.email}")
    return {"message": "Email verified successfully. You can now log in."}


# --------------------------------------------------------------------------- #
#  Resend OTP                                                                   #
# --------------------------------------------------------------------------- #

@router.post("/resend-otp", status_code=200)
def resend_otp(body: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resend a fresh OTP for email verification or password reset."""
    user = db.query(User).filter(User.email == body.email).first()
    if user is None:
        # Don't reveal if email exists — return same message either way
        return {"message": "If that email exists, a new OTP has been sent."}

    code = create_otp(user_id=user.id, purpose=body.purpose, db=db)
    send_otp_email(to_email=user.email, code=code, purpose=body.purpose)

    return {"message": "A new OTP has been sent to your email."}


# --------------------------------------------------------------------------- #
#  Login                                                                        #
# --------------------------------------------------------------------------- #

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email + password.
    Returns a JWT access token valid for 24 hours.
    """
    user = db.query(User).filter(User.email == body.email).first()

    # Use constant-time comparison to prevent timing attacks
    if user is None or not verify_password(body.password, user.hashed_password):
        raise AuthError("Invalid email or password.")

    if not user.is_verified:
        raise UserNotVerifiedError(
            "Your email is not verified. "
            "Check your inbox for the OTP or use /resend-otp."
        )

    token = create_access_token(user_id=user.id)
    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
    )


# --------------------------------------------------------------------------- #
#  Forgot password                                                              #
# --------------------------------------------------------------------------- #

@router.post("/forgot-password", status_code=200)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send a password-reset OTP to the email.
    Always returns same message to avoid email enumeration.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        code = create_otp(user_id=user.id, purpose="reset_password", db=db)
        send_otp_email(to_email=user.email, code=code, purpose="reset_password")
        logger.info(f"Password reset OTP sent: {user.email}")

    return {
        "message": "If that email is registered, a password reset OTP has been sent."
    }


# --------------------------------------------------------------------------- #
#  Reset password                                                               #
# --------------------------------------------------------------------------- #

@router.post("/reset-password", status_code=200)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Set a new password using the OTP received via forgot-password.
    """
    user = db.query(User).filter(User.email == body.email).first()
    if user is None:
        raise AuthError("No account found with this email.")

    verify_otp(user_id=user.id, code=body.otp, purpose="reset_password", db=db)

    user.hashed_password = hash_password(body.new_password)
    db.commit()

    logger.info(f"Password reset successful: {user.email}")
    return {"message": "Password reset successfully. You can now log in."}


# --------------------------------------------------------------------------- #
#  Me (current user profile)                                                   #
# --------------------------------------------------------------------------- #

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently logged-in user."""
    return UserProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )
