"""
FastAPI dependencies for authentication.
Import get_current_user into any route that requires a logged-in user.
"""

import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models.db import get_db, User
from app.services.auth_service import decode_access_token
from app.core.exceptions import AuthError

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)  # auto_error=False lets us control the error response


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate JWT from Authorization: Bearer <token>.
    Returns the User ORM object.
    Raises AuthError (→ 401) if token is missing, invalid, or expired.
    """
    if credentials is None:
        raise AuthError("Not authenticated. Provide Authorization: Bearer <token>.")
    
    token = credentials.credentials
    user_id = decode_access_token(token)  # raises AuthError if invalid/expired
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthError("User account not found.")
    return user
