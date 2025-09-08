import pytest
from fastapi.testclient import TestClient

import psycopg2
from psycopg2.extras import RealDictCursor
from db.database import Storage
from db.database import get_db
from unittest.mock import MagicMock

from app.main import app

from app import oath2

TEST_DSN = "host=localhost dbname=test_db user=testuser password=1234"

@pytest.fixture(scope="session", autouse=True)
def startup_db():
    # runs once before any tests
    conn = psycopg2.connect(TEST_DSN, cursor_factory=RealDictCursor)
    db = Storage(connection=conn)
    db.drop_database()
    db.create_tables_if_not_exist()
    yield
    db.close()

def override_get_db():
    conn = psycopg2.connect(TEST_DSN, cursor_factory=RealDictCursor)
    db = Storage(connection=conn)
    db.create_tables_if_not_exist()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user_id():
    return {"id": 1, "email": "test@test.com"}

app.dependency_overrides[oath2.get_current_user_id] = override_get_current_user_id
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_author_unit():
    mock_db = MagicMock()
    mock_db.insert_authors.return_value = {"id": 1, "firstname": "Isaac", "lastname": "Asimov"}

    app.dependency_overrides[lambda: Storage] = lambda: mock_db
    app.dependency_overrides[lambda: "auth"] = lambda: {"id": 1, "email": "test@test.com"}

    response = client.post(
        "/authors",
        json={"firstname": "Isaac", "lastname": "Asimov"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["author"]["firstname"] == "Isaac"
    assert data["author"]["lastname"] == "Asimov"

def test_create_author():
    response = client.post(
        "/authors",
        json={
            "firstname": "Frank",
            "lastname": "Herbert"
        },
        headers={"Authorization": "Bearer testtoken"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "author" in data
    assert data["author"]["firstname"] == "Frank"
    assert data["author"]["lastname"] == "Herbert"


def test_create_genre():
    response = client.post(
        "/genres",
        json={
            "name_genre": "Sci-Fi"
        },
        headers={"Authorization": "Bearer testtoken"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["name_genre"] == "Sci-Fi"


def test_create_book():
    response = client.post(
        "/books",
        json={
            "title": "Dune",
            "description": "Epic science fiction novel",
            "published_year": 1965,
            "price": 9.99,
            "genre_id": 1,
            "author_id": 1
        },
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "book" in data
    assert data["book"]["title"] == "Dune"

if __name__ == "__main__":
    override_get_db()