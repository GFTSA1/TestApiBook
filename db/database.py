import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class Storage:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            cursor_factory=RealDictCursor,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()

    def drop_database(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS author CASCADE")
            cursor.execute("DROP TABLE IF EXISTS genre CASCADE")
            cursor.execute("DROP TABLE IF EXISTS book CASCADE")
            self.connection.commit()

    def create_tables_if_not_exist(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS author (
                Id SERIAL PRIMARY KEY,
                firstname VARCHAR(255),
                lastname VARCHAR(255),
                UNIQUE(firstname, lastname)
            );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS genre (
                Id SERIAL PRIMARY KEY,
                name_genre VARCHAR(255) UNIQUE
            );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS book (
            Id SERIAL PRIMARY KEY,
            title VARCHAR(255) UNIQUE,
            description TEXT,
            published_year INTEGER,
            price REAL,
            genre_id INTEGER,
            author_id INTEGER,
            FOREIGN KEY(author_id) REFERENCES author(id),
            FOREIGN KEY(genre_id) REFERENCES genre(id)
            );""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                Id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            );""")

            self.connection.commit()

    def insert_book(self, book):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO book (title, description, published_year, price, genre_id, author_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    f"{book.title}",
                    f"{book.description}",
                    f"{book.published_year}",
                    f"{book.price}",
                    f"{book.genre_id}",
                    f"{book.author_id}",
                ),
            )
            book = cursor.fetchone()
        return book

    def insert_book_in_bulk(self, book):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO book (title, description, published_year, price, genre_id, author_id) VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    f"{book[0]}",
                    f"{book[1]}",
                    f"{book[2]}",
                    f"{book[3]}",
                    f"{book[4]}",
                    f"{book[5]}",
                ),
            )

    def retrieve_book_for_title(self, title):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM book WHERE title = %s""", (title,))
            book = cursor.fetchone()
        return book

    def create_user(self, user):
        with self.connection.cursor() as cursor:
            cursor.execute("""INSERT INTO users (email, password) VALUES (%s, %s) RETURNING email""", (user.email, user.password))
            user = cursor.fetchone()
        return user

    def retrieve_user_by_id(self, id):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM users WHERE id = %s""", (str(id),))
            user = cursor.fetchone()
        return user

    def retrieve_user_by_email(self, email):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM users WHERE email LIKE %s""", (f'{email}',))
            user = cursor.fetchone()
        return user

    def insert_many_books(self, books):
        with self.connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO book (title, description, published_year, price, genre_id, author_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
                """,
                books
            )
            result = cursor.fetchall()
        return result

    def retrieve_books(self, query_set):
        with self.connection.cursor() as cursor:
            conditions = []
            params = []
            query_sql = """SELECT * FROM book"""

            if query_set.title is not None:
                conditions.append("title LIKE %s")
                params.append(f"%{query_set.title}%")

            if query_set.description is not None:
                conditions.append("description LIKE %s")
                params.append(f"%{query_set.description}%")

            if query_set.published_year_start is not None:
                conditions.append("published_year >= %s")
                params.append(query_set.published_year_start)

            if query_set.published_year_end is not None:
                conditions.append("published_year <= %s")
                params.append(query_set.published_year_end)

            if query_set.author_id is not None:
                conditions.append("author_id = %s")
                params.append(query_set.author_id)

            if query_set.genre_id is not None:
                conditions.append("genre_id = %s")
                params.append(query_set.genre_id)

            if conditions:
                query_sql = query_sql + " WHERE " + " AND ".join(conditions)

            cursor.execute(query_sql, params)
            results = cursor.fetchall()
        return results

    def retrieve_authors(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM author""")
            results = cursor.fetchall()
        return results

    def retrieve_author_by_id(self, author_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM author WHERE id = %s""", (str(author_id),))
            results = cursor.fetchone()
        return results

    def retrieve_author_for_firstname_and_lastname(self, firstname, lastname):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM author WHERE firstname = %s AND lastname = %s""",
                (firstname, lastname),
            )
            results = cursor.fetchone()
        return results

    def retrieve_genre(self, genre_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM genre WHERE id = %s""", (str(genre_id),))
            results = cursor.fetchone()
        return results

    def retrieve_genre_by_title(self, genre_name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM genre WHERE name_genre = %s""", (genre_name,)
            )
            results = cursor.fetchone()
        return results

    def insert_authors(self, author):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO author (firstname, lastname) VALUES (%s, %s) RETURNING *;""",
                (f"{author.firstname}", f"{author.lastname}"),
            )
            cursor.fetchone()
        return author

    def insert_genres(self, genre):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO genre (name_genre) VALUES (%s) RETURNING name_genre;""",
                (f"{genre.name_genre}",),
            )
            cursor.fetchone()
        self.connection.commit()
        return genre

    def delete_book(self, book_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """DELETE FROM book WHERE id = %s RETURNING *""", (str(book_id),)
            )
            deleted_book = cursor.fetchone()
        return deleted_book

    def update_book(self, book_id, book):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE book SET title = %s, published_year = %s, genre_id = %s, author_id = %s WHERE id = %s RETURNING *""",
                (
                    book.title,
                    book.published_year,
                    book.genre_id,
                    book.author_id,
                    str(book_id),
                ),
            )
            book_updated = cursor.fetchone()
        return book_updated


if __name__ == "__main__":
    db = Storage()
    db.drop_database()
    db.create_tables_if_not_exist()
