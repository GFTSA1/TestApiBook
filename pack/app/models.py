from datetime import date
from traceback import print_tb

from fastapi import HTTPException
from pydantic import BaseModel, conint, field_validator, model_validator, EmailStr
from typing import Optional

from db.database import Storage


class Author(BaseModel):
    firstname: str
    lastname: str

    @model_validator(mode="before")
    @classmethod
    def unique_validator(cls, data):
        db = Storage()
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        author = db.retrieve_author_for_firstname_and_lastname(firstname, lastname)
        if author is not None:
            raise HTTPException(status_code=400, detail="Author already exists")
        return data


class UserBase(BaseModel):
    email: EmailStr
    password: str


class Genre(BaseModel):
    name_genre: str

    @field_validator("name_genre")
    def validate_name_genre(cls, value):
        db = Storage()
        genre = db.retrieve_genre_by_title(value)
        if genre is not None:
            raise HTTPException(status_code=400, detail="Genre already exists")
        return value


class Book(BaseModel):
    title: str
    description: str
    published_year: conint(gt=0, le=date.today().year)
    price: float
    genre_id: int
    author_id: int

    @model_validator(mode="before")
    def validatator(cls, values):
        db = Storage()
        title_name = values.get("title")
        description = values.get("description")
        author_id = values.get("author_id")
        genre_id = values.get("genre_id")

        if len(title_name) == 0:
            raise HTTPException(status_code=400, detail="Title cannot be empty")

        if len(description) == 0:
            raise HTTPException(status_code=400, detail="Description cannot be empty")

        title_name = db.retrieve_book_for_title(title_name)
        if title_name is not None:
            raise HTTPException(
                status_code=400, detail="Book with such title already exists"
            )

        author = db.retrieve_author_by_id(author_id)
        if author is None:
            raise HTTPException(status_code=400, detail="Author not found")

        genre = db.retrieve_genre(genre_id)
        if genre is None:
            raise HTTPException(status_code=400, detail="Genre not found")
        return values


class QueryParams(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    published_year_start: Optional[int] = None
    published_year_end: Optional[int] = None
    genre_id: Optional[int] = None
    author_id: Optional[int] = None
    sort_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
