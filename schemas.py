from pydantic import BaseModel


class LinkBase(BaseModel):
    pass


class LinkCreate(LinkBase):
    long_version: str


class Link(LinkBase):
    id: int
    long_version: str
    short_version: str
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    user_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    links: list[Link] = []

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    old_user_name: str
    user_name: str
    old_password: str
    password: str

    class Config:
        orm_mode = True


class UserAuth(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str
