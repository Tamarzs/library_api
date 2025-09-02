from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_db, get_current_user
from app.assets.tables import Borrows, Books, Users

router = APIRouter(
    tags=["Borrows"],
    prefix="/borrows",
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def borrow_book(db: db_dependency, user: user_dependency, book_id: int):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    borrowed_book = db.query(Books).filter(Books.id == book_id).first()
    verify_user = db.query(Users).filter(user.get('id') == Users.id).first()

    if borrowed_book.available_copies == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available copies for this book.")

    elif verify_user.borrowed_books == 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Borrowed books limit reached.")

    else:
        borrowed_book.available_copies -= 1
        verify_user.borrowed_books += 1

        db.commit()


    if not borrowed_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found.")

    borrow = Borrows(

        user_id=user.get('id'),
        book_id=book_id,
        book_title=borrowed_book.title,
        book_author=borrowed_book.author,
        borrow_date=datetime.now(timezone.utc),
        return_date=datetime.now(timezone.utc) + timedelta(days=5),

    )

    db.add(borrow)
    db.commit()

    return db.query(Borrows).filter(Borrows.user_id == user.get('id')).first()


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def return_book(db: db_dependency, user: user_dependency, book_id: int):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    returned_book = db.query(Books).filter(Books.id == book_id).first()
    user_borrow = db.query(Borrows).filter(Borrows.user_id == user.get('id')).first()
    user = db.query(Users).filter(Users.id == user.get('id')).first()

    if user.borrowed_books == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books to return.")

    if user_borrow.book_id == book_id:

        returned_book.available_copies += 1
        user.borrowed_books -= 1
        db.delete(user_borrow)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have not borrowed this book.")


@router.get("", status_code=status.HTTP_200_OK)
async def get_borrows(db: db_dependency, user: user_dependency):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    verify_user = db.query(Users).filter(user.get('id') == Users.id).first()

    if verify_user.borrowed_books == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No borrowed books yet!")

    return db.query(Borrows).filter(Borrows.user_id == user.get('id')).all()
