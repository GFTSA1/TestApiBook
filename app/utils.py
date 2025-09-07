from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify_password(password_to_check, hashed_password):
    return pwd_context.verify(password_to_check, hashed_password)
