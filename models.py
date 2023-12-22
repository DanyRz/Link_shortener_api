import passlib.hash
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """ORM class for User instances"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    hashed_password = Column(String)

    def verify_password(self, password: str):
        """Verifies password"""
        return passlib.hash.bcrypt.verify(password, self.hashed_password)

    links = relationship("Link", back_populates="owner")


class Link(Base):
    """ORM class for Link instances"""
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    long_version = Column(String)
    short_version = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="links")
