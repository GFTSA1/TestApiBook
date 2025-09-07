import os

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from db.database import get_db
import json
import io
from unittest.mock import patch, MagicMock

from app.main import app
from app.models import Book, Author, Genre, UserBase

from app import oath2, utils

DATABASE_URL = 'sqlite:///:memory:'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_author():
    response = client.post('/authors', json={'first_name': 'John', 'last_name': 'Doe'})
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED

def create_sqlite_db(db):
    db.conn.execute("PRAGMA foreign_keys = ON;")  # enable foreign keys
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            UNIQUE(firstname, lastname)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_genre TEXT UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            description TEXT,
            published_year INTEGER,
            price REAL,
            genre_id INTEGER,
            author_id INTEGER,
            FOREIGN KEY(author_id) REFERENCES author(id),
            FOREIGN KEY(genre_id) REFERENCES genre(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        );
    """)

    conn.commit()
    conn.close()
    print(f"SQLite database created at {db_path}")

if __name__ == "__main__":
    create_sqlite_db()