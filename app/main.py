from fastapi import FastAPI

from .routers import auth, users, books


app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)