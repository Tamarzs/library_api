from datetime import datetime, timedelta, timezone

from ...app.database.settings import (Base)
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    borrowed_books = Column(Integer, default=0)


class Books(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True)
    author = Column(String)
    genre = Column(String)
    available_copies = Column(Integer)
    is_active = Column(Boolean, default=True)


class Borrows(Base):
    __tablename__ = 'borrows'

    borrow_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    book_title = Column(String)
    book_author = Column(String)
    borrow_date = Column(String, default=datetime.now(timezone.utc))
    return_date = Column(String, default=datetime.now(timezone.utc) + timedelta(days=5))