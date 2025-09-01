from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from app.database.settings import SessionLocal
from app.assets.models import TokenModel
from app.assets.tables import Users

from passlib.context import CryptContext
from jose import jwt, JWTError


router = APIRouter(
    tags=['Auth'],
    prefix="/auth",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

SECRET_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJzdWIiOiJ0YW1hcnoiLCJpZCI6MSwiZXhwIjoxNzU2MjM1NTk2fQNLGCBMFuUr17HyTGXwprNopdqdbPPcU3ANyu98biXoE'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):

    encode = {'sub': username, 'id': user_id,}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires},)
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

        return {'username': username, 'id': user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/login', response_model=TokenModel, status_code=status.HTTP_200_OK)
async def login(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):

    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(username=user.username, user_id=user.id, expires_delta=timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}
