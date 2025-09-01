from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_db, get_current_user
from app.assets.tables import Users
from app.assets.models import UserModel

from passlib.context import CryptContext


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency, user: user_dependency):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()

    if not verify_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    if verify_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    return db.query(Users).filter(Users.is_active == True).all()


@router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency, username: str):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).filter(Users.is_active == True).first()

    if not verify_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    if verify_user.role != 'admin' and verify_user.username == username:
        return db.query(Users).filter(Users.username == user.get('username')).filter(Users.is_active == True).first()

    elif verify_user.role == 'admin':
        return db.query(Users).filter(Users.username == username).filter(Users.is_active == True).first()

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")


@router.put("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, user: user_dependency, updated_user: UserModel, username: str):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()
    permission = False

    if not verify_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    if verify_user.role == 'admin': permission = True
    if verify_user.role != 'admin' and verify_user.username == username: permission = True

    if permission:

        user_model = db.query(Users).filter(Users.username == username).first()

        user_model.username = updated_user.username
        user_model.email = updated_user.email
        user_model.hashed_password = bcrypt_context.hash(updated_user.password)
        user_model.role = updated_user.role if verify_user.role == 'admin' else 'user'

        db.add(user_model)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found.")


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, username: str):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()
    permission = False

    if not verify_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    if verify_user.role == 'admin': permission = True
    if verify_user.role != 'admin' and verify_user.username == username: permission = True

    if permission:

        inactive = db.query(Users).filter(Users.username == username).first()
        inactive.is_active = False

        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")