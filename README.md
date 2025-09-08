Test Api Book

Install with:

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

The project is also deployed on lambda: 
https://5fbfgdraug4dmgoqtmmrvgjq6u0wcfcf.lambda-url.us-east-1.on.aws/

The .env file configuration has been passed to HR.

Important note is that genre_id and author_id are book fk, so firstly create them, and only after insert books.

There are also postman collection attached for convenience of testing requests.

Endpoints are:

GET:

books/ - retrieve all book, filters, paggination and sorting included

books/recomendations-genre/{genre_id} - recommendations by genre_id

books/recomendations-author/{author_id} - recommendations by author_id

authors/ - retrieve all authors 

POST:

books/ - create book

books/import/ - create books from csv/json

authors/ - create author

genres/ - create genre

register/ - create user

login/ - logins created user

PUT:

books/{book_id}/ - update book by id 

DELETE:

books/{book_id}/ - delete book by id

