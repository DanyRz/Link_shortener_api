from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


SECRET_KEY = 'PLEASE_ENTER_YOUR_SECRET_KEY_HERE'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


def get_password_hash(password: str) -> str:
    """hash a password"""
    return pwd_context.hash(password)
