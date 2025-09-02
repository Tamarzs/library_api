from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_db, get_current_user
from app.assets.tables import Books, Users
from app.assets.models import BookModel


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def read_all_books(db: db_dependency,user: user_dependency):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    return db.query(Books).filter(Books.is_active == True).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(db: db_dependency, user: user_dependency, created_book: BookModel):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()

    if verify_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    created_book = Books(

        title=created_book.title,
        author=created_book.author,
        genre=created_book.genre,
        available_copies=created_book.available_copies,

    )

    db.add(created_book)
    db.commit()


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(db: db_dependency, user: user_dependency, updated_book: BookModel, book_id: int):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()

    if verify_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    book_model = db.query(Books).filter(Books.id == book_id).first()

    if book_model:
        book_model.title = updated_book.title
        book_model.author = updated_book.author
        book_model.genre = updated_book.genre
        book_model.available_copies = updated_book.available_copies

        db.add(book_model)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: db_dependency, user: user_dependency, book_id):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(Users.id == user.get('id')).first()

    if verify_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")

    book_model = db.query(Books).filter(Books.id == book_id).first()

    if not book_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

    book_model.is_active = False
    db.commit()