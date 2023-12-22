from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from jose import jwt

import validators

import crud
import models
import schemas
import auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    """Dependency injection for db"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    """Retrieves current user using JWT token"""
    credential_exception = HTTPException(status_code=401, detail='Unable to validate credentials')
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        current_user_id = payload.get('id')
        current_user = crud.get_user_by_id(db, user_id=int(current_user_id))
    except Exception:
        raise credential_exception
    return current_user


@app.get('/')
def home():
    """Home page endpoint"""
    return {'msg': 'Hello'}


# Endpoints for future admin:

@app.get("/admin/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Endpoint to get all User instances"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/admin/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Endpoint to get a User instance by id"""
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Endpoint to delete User instance by id"""
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user_by_id(db, user_id=user_id)
    return {"message": "user deleted"}


@app.get("/admin/links/", response_model=list[schemas.Link])
def read_links(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Endpoint to get all Link instances"""
    links = crud.get_links(db, skip=skip, limit=limit)
    return links


@app.get("/admin/links/{link_id}", response_model=schemas.Link)
def read_link(link_id: int, db: Session = Depends(get_db)):
    """Endpoint to get a Link instance by id"""
    db_link = crud.get_link_by_id(db, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link


@app.delete("/admin/links/{link_id}")
def delete_link(link_id: int, db: Session = Depends(get_db)):
    """Endpoint to delete Link instance by id"""
    db_link = crud.get_link_by_id(db, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    crud.delete_link(db, link_id=link_id)
    return {"message": "link deleted"}


# Endpoints for user self actions:

@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint for registration of a new User instance"""
    db_user = crud.get_user_by_user_name(db, user_name=user.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint to get a JWT token by login"""
    db_user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail='Incorrect credentials')
    access_token_expires = crud.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(data={'id': db_user.id}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post("/refresh_token", response_model=schemas.Token)
def get_new_access_token(current_user: schemas.User = Depends(get_current_user)):
    """Endpoint to get a new token while logged in"""
    access_token_expires = crud.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(data={'id': current_user.id}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get("/users/me", response_model=schemas.User)
def get_user_info(current_user: schemas.User = Depends(get_current_user)):
    """Get credentials of logged-in user"""
    return current_user


@app.patch("/users/me/update", response_model=schemas.User)
def update_user_credentials(user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update credentials of a user"""
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not crud.authenticate_user(db, user.old_user_name, user.old_password):
        raise HTTPException(status_code=401, detail="Invalid old credentials")
    return crud.update_user(db=db, user=user, old_user_name=user.old_user_name, user_name=user.user_name)


@app.delete("/users/me/delete")
def delete_current_user(user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete logged-in user's account"""
    crud.delete_user(db, user=user)
    return {"message": "user deleted"}


# Endpoints for user interacting with own links:

@app.get("/users/me/links", response_model=list[schemas.Link])
def read_user_links(user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve logged-in user's links"""
    user_links = crud.get_user_links(db, user_id=user.id)
    return user_links


@app.get("/users/me/{link_id}", response_model=schemas.Link)
def read_user_link(link_id: int, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve specific link of current user by is"""
    user_link = crud.get_user_link_by_id(db, user_id=user.id, link_id=link_id)
    if user_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return user_link


@app.post("/users/me/links/create", response_model=schemas.Link)
def create_link(link: schemas.LinkCreate, db: Session = Depends(get_db),
                current_user: schemas.User = Depends(get_current_user)):
    """Create a new Link instance"""
    if not validators.url(link.long_version):
        raise HTTPException(status_code=422, detail="Wrong input")
    return crud.create_link(db=db, link=link, current_user=current_user)


@app.delete("/users/me/links/delete/{link_id}")
def delete_link(link_id: int, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete user's link selected by id"""
    db_link = crud.get_link_by_id(db, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    if db_link not in user.links:
        raise HTTPException(status_code=403, detail="Link is not your own")
    crud.delete_link(db, link_id=link_id)
    return {"message": "link deleted"}


@app.get('/{shortener}')
def get_target_url(shortener: str, db: Session = Depends(get_db)):
    """Redirect short url to original page"""
    db_link = crud.get_link_by_shortener(db, shortener=shortener)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    if db_link:
        return RedirectResponse(db_link.long_version)
