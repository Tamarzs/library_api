from app.database.settings import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)


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

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    borrow_date = Column(String)
    return_date = Column(String)