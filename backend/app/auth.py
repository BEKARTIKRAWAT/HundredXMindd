from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, User
import uuid
import os
# ------------------------------------------------------------------
# 1. Configuration (use strong secret in production)
# ------------------------------------------------------------------
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-very-strong-secret-min-32-chars-fallback")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
# ------------------------------------------------------------------
import bcrypt
# 2. Password utilities (direct bcrypt)
# ------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt truncates at 72 bytes automatically, but we explicitly truncate
    truncated = plain_password[:72].encode('utf-8')
    return bcrypt.checkpw(truncated, hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    truncated = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(truncated, salt).decode('utf-8')
# ------------------------------------------------------------------
# 3. Token creation
# ------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# ------------------------------------------------------------------
# 4. Database helpers
# ------------------------------------------------------------------
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()
def store_refresh_token(db: Session, user_id: str, refresh_token: str):
    # Store refresh token in session table (or separate refresh_tokens table)
    from database import Session as SessionModel
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db_session = SessionModel(id=refresh_token, user_id=user_id, expires_at=expires_at)
    db.add(db_session)
    db.commit()
def revoke_refresh_token(db: Session, refresh_token: str):
    from database import Session as SessionModel
    db.query(SessionModel).filter(SessionModel.id == refresh_token).delete()
    db.commit()
def is_refresh_token_valid(db: Session, refresh_token: str) -> bool:
    from database import Session as SessionModel
    record = db.query(SessionModel).filter(SessionModel.id == refresh_token).first()
    return record is not None and record.expires_at > datetime.now(timezone.utc)
# ------------------------------------------------------------------
# 5. Authentication dependency
# ------------------------------------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(lambda: SessionLocal())
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_id(db, user_id)
    if not user.is_active:
        raise credentials_exception
    if user is None:
        raise credentials_exception
    return user
# Optional: get current user or None (for optional auth)
async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(lambda: SessionLocal())
):
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
