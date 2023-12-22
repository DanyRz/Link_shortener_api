from sqlalchemy.orm import Session
from secrets import token_urlsafe
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

import models
import schemas
import auth


domain: str = 'http://127.0.0.1:8000/'


def create_shortener() -> str:
    """Creates a random short link"""
    shortener = token_urlsafe(5)
    return f'{domain}{shortener}'


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieves all User instances"""
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_user_name(db: Session, user_name: str):
    """Retrieves User instance by user_name attribute"""
    return db.query(models.User).filter(models.User.user_name == user_name).first()


def get_user_by_id(db: Session, user_id: int):
    """Retrieves User instance by id attribute"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def delete_user_by_id(db: Session, user_id: int):
    """Deletes User instance, found by id attribute"""
    db_user = db.get(models.User, user_id)
    for link in db_user.links:
        delete_link(db, link_id=link.id)
    db.delete(db_user)
    db.commit()
    return None


def create_user(db: Session, user: schemas.UserCreate):
    """Creates a User instance"""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(user_name=user.user_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(old_user_name: str, user_name: str, db: Session, user: schemas.UserUpdate):
    """Allows for updating user credentials"""
    hashed_password = auth.get_password_hash(user.password)
    user = db.query(models.User).filter(models.User.user_name == old_user_name).first()
    user.hashed_password = hashed_password
    user.user_name = user_name
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user):
    """Deletes User instance"""
    for link in user.links:
        delete_link(db, link_id=link.id)
    db.delete(user)
    db.commit()
    return None


def get_user_links(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Retrieves Link instances of a selected user"""
    return db.query(models.Link).filter(models.Link.owner_id == user_id).offset(skip).limit(limit).all()


def create_link(db: Session, link: schemas.LinkCreate, current_user):
    """Creates Link instance"""
    short_version = create_shortener()
    db_link = models.Link(long_version=link.long_version, short_version=short_version, owner_id=current_user.id)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def get_links(db: Session, skip: int = 0, limit: int = 100):
    """Retrieves all Link instances"""
    return db.query(models.Link).offset(skip).limit(limit).all()


def get_link_by_id(db: Session, link_id: int):
    """Retrieves Link instance by id"""
    return db.query(models.Link).filter(models.Link.id == link_id).first()


def get_link_by_shortener(db: Session, shortener: str):
    """Retrieves link by short part, used for redirecting to original """
    return db.query(models.Link).filter(models.Link.short_version == f'{domain}{shortener}').first()


def delete_link(db: Session, link_id: int):
    """Deletes Link instance"""
    db_link = db.get(models.Link, link_id)
    db.delete(db_link)
    db.commit()
    return None


def get_user_link_by_id(db: Session, user_id: int, link_id: int):
    """Retrieves one of users links selected by id"""
    return db.query(models.Link).filter(models.Link.id == link_id, models.Link.owner_id == user_id).first()


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    """Creates a JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, user_name: str, password: str):
    """Authenticates user"""
    db_user = get_user_by_user_name(db, user_name)
    if not db_user:
        raise HTTPException(status_code=401, detail='Unable to validate credentials')
    if not db_user.verify_password(password):
        raise HTTPException(status_code=401, detail='Unable to validate credentials')
    return db_user
