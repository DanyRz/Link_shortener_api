from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

from main import app, get_db


DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


client = TestClient(app)


def get_test_db():
    """Override of db dependency injection from main"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


def setup():
    """Initializes a mock database for testing"""
    Base.metadata.create_all(bind=engine)


def test_read_root():
    """Simple test - reading a home endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'msg': 'Hello'}


def test_create_user():
    """Tests registration endpoint"""
    response = client.post('/register', json={"user_name": "Joe",
                                              "password": "sleepy"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["user_name"] == "Joe"
    assert data["links"] == []


def test_create_duplicate_user():
    """Tests if creation of users with already existing username is forbidden"""
    response = client.post('/register', json={"user_name": "Joe",
                                              "password": "sleepy2"})
    assert response.status_code == 400, "Username already registered"


def test_read_user():
    """Validates if retrieving user data works correctly"""
    response = client.post(
        "/register", json={"user_name": "Don", "password": "hairy"}
    )
    assert response.status_code == 200
    data = response.json()
    user_id = data["id"]

    response = client.get(f"admin/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "Don"
    assert data["links"] == []
    assert data["id"] == user_id


def teardown():
    """Destroys mock database after testing"""
    Base.metadata.drop_all(bind=engine)
