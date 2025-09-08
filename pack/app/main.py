from dns.e164 import query
from fastapi import FastAPI, HTTPException, status, Response, UploadFile, File
from fastapi.params import Depends
from app import utils, oath2
import csv, json, io
from .models import Author, Genre, Book, QueryParams, Token, UserBase
from db.database import Storage, get_db
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

@app.get("/books")
async def root(query: QueryParams = Depends(), db: Storage = Depends(get_db)):
    with Storage() as db:
        books = db.retrieve_books(query)
    return {"data": books}


@app.post("/books")
async def create_book(book: Book, current_user: UserBase = Depends(oath2.get_current_user_id), db: Storage = Depends(get_db)):
    book = db.insert_book(book)
    return {"book": book}

@app.post("/books/import")
async def import_books(
    json_file: UploadFile | None = File(default=None),
    csv_file: UploadFile | None = File(default=None),
    db: Storage = Depends(get_db)
):
    if not json_file and not csv_file:
        raise HTTPException(status_code=400, detail="Provide at least one file (JSON or CSV)")

    data = []

    if json_file:
        content = await json_file.read()
        try:
            books = json.loads(content.decode("utf-8"))
            for b in books:
                book = Book(**b)
                data.append((
                    book.title,
                    book.description,
                    book.published_year,
                    book.price,
                    book.genre_id,
                    book.author_id
                ))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

    if csv_file:
        content = await csv_file.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        for row in reader:
            try:
                book = Book(**row)
                data.append((
                    book.title,
                    book.description,
                    book.published_year,
                    book.price,
                    book.genre_id,
                    book.author_id
                ))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid CSV row: {row} ({e})")

    if not data:
        raise HTTPException(status_code=400, detail="No valid books found")

    for book in data:
        db.insert_book_in_bulk(book)

    return {"imported": data}


@app.get("/books/recomendations-genre/{genre_id}")
async def get_recommendations(genre_id, db: Storage = Depends(get_db)):
    books = db.recommend_books_by_genre(genre_id)
    return {"data": books}

@app.get("/books/recomendations-author/{author_id}")
async def get_recommendations(author_id, db: Storage = Depends(get_db)):
    books = db.recommend_books_by_author(author_id)
    return {"data": books}

@app.get("/authors")
async def retrieve_author(db: Storage = Depends(get_db)):
    authors = db.retrieve_authors()
    return {"authors": authors}


@app.post("/authors")
async def create_author(author: Author, current_user: UserBase = Depends(oath2.get_current_user_id), db: Storage = Depends(get_db)):

    author = db.insert_authors(author)
    return {"author": author}


@app.post("/genres")
async def create_genre(genre: Genre, current_user: UserBase = Depends(oath2.get_current_user_id), db: Storage = Depends(get_db)):
    genre = db.insert_genres(genre)
    return {"data": genre}


@app.delete("/books/{book_id}")
async def delete_book_id(book_id: int, current_user: UserBase = Depends(oath2.get_current_user_id), db: Storage = Depends(get_db)):
    deleted_book = db.delete_book(book_id)
    if deleted_book is None:
        raise HTTPException(status_code=404, detail=f"Book with {book_id} not found")

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": f"Book was deleted successfully"},
    )


@app.put("/books/{book_id}")
async def update_book_id(book_id: int, book: Book, current_user: UserBase = Depends(oath2.get_current_user_id), db: Storage = Depends(get_db)):
    updated_book = db.update_book(book_id, book)
    if updated_book is None:
        raise HTTPException(status_code=404, detail=f"Book with {book_id} not found")

    return {"book": updated_book}


@app.post('/register', status_code=status.HTTP_201_CREATED)
def create_user(user: UserBase, db: Storage = Depends(get_db)):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = db.create_user(user)
    return new_user


@app.post("/login", response_model=Token)
def login(user_credentials: UserBase, db: Storage = Depends(get_db)):
    user = db.retrieve_user_by_email(user_credentials.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    if not utils.verify_password(user_credentials.password, user.get('password')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Credentials")
    access_token = oath2.create_access_token(data={"user_id":user.get('id')})
    return {'access_token': access_token, 'token_type': 'bearer'}
