import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlmodel import Session, select
from models.user_model import User
from schemas.auth_schema import TokenData, TokenPair

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

password_hash = PasswordHash.recommended()

class AuthServices:
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return password_hash.verify(plain, hashed)

    @staticmethod
    def authenticate_user(session: Session, username: str, password: str) -> User:
        user = session.exec(select(User).where(User.username == username)).first()
        error = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if not user or not AuthServices.verify_password(password, user.hashed_password):
            raise error
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(username: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return jwt.encode(
            {"sub": username, "exp": expire, "type": "refresh"},
            SECRET_KEY, algorithm=ALGORITHM
        )

    @staticmethod
    def decode_refresh_token(token: str) -> str:
        err = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise err
            username: str | None = payload.get("sub")
            if not username:
                raise err
            return username
        except jwt.InvalidTokenError:
            raise err

    @staticmethod
    def decode_access_token(token: str) -> TokenData:
        err = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") == "refresh":
                raise err
            username: str | None = payload.get("sub")
            if not username:
                raise err
            return TokenData(username=username)
        except jwt.InvalidTokenError:
            raise err
