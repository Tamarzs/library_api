from fastapi import FastAPI

from .routers import auth, users, books, borrows


app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(borrows.router)