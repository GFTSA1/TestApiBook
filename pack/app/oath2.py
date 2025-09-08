import os

from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException

from db.database import Storage
from app.models import TokenData
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = f"{os.getenv('SECRET_KEY')}"
ALGORITHM = f"{os.getenv('ALGORITHM')}"
ACCESS_TOKEN_EXPIRE_MINUTES = int(f"{os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')}")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user_id(
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)
    with Storage() as db:
        user = db.retrieve_user_by_id(token.id)
    return user
