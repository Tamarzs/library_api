from pydantic import BaseModel, Field


class UserModel(BaseModel):

    username: str = Field(min_length=2, max_length=50, examples=["Tama"])
    email: str = Field(min_length=2, max_length=50, examples=["email@email.com"])
    password: str = Field(min_length=2, max_length=50, examples=["password"])


class BookModel(BaseModel):

    title: str = Field(min_length=2, max_length=50, examples=["My first book"])
    author: str = Field(min_length=2, max_length=50, examples=["Tama"])
    genre: str = Field(min_length=2, max_length=50, examples=["Horror"])
    available_copies: int = Field(gt=-1, examples=[2])


class TokenModel(BaseModel):

    access_token: str
    token_type: str