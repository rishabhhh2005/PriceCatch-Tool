import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_session
from backend.auth import seed_default_api_key, hash_key
from backend.models import ApiKey

TEST_DATABASE_URL = "sqlite:///./test_pricecatch.db"

# Patch SessionLocal across all modules
eng = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)

import backend.database
backend.database.engine = eng
backend.database.SessionLocal = TestingSessionLocal
backend.database.DATABASE_URL = TEST_DATABASE_URL

@pytest.fixture(scope="session")
def engine():
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose() # Fix for Windows DB cleanup permission error
    Base.metadata.drop_all(bind=eng)
    if os.path.exists("test_pricecatch.db"):
        try:
            os.remove("test_pricecatch.db")
        except PermissionError:
            pass

@pytest.fixture(scope="session")
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    # Seed default API key
    key_hash = hash_key("dev-key-12345")
    if not session.query(ApiKey).filter(ApiKey.key_hash == key_hash).first():
        session.add(ApiKey(key_hash=key_hash, name="Test Key"))
        session.commit()
    yield session
    session.close()

@pytest.fixture(scope="session")
def client(engine, db_session):
    from backend.main import app
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_session():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "dev-key-12345"}

@pytest.fixture
def grailed_raw():
    return {
        "product_id": "test-grailed-001",
        "brand": "amiri",
        "model": "Amiri Test Shirt",
        "price": 425.0,
        "image_url": "https://example.com/img.jpg",
        "product_url": "https://grailed.com/listings/123",
        "metadata": {"is_sold": False, "color": "Black", "style": "Street"},
        "function_id": "apparel_authentication"
    }

@pytest.fixture
def fashionphile_raw():
    return {
        "product_id": "test-fashionphile-001",
        "brand": "Tiffany",
        "model": "Tiffany Hoop Earrings",
        "price": 1480.0,
        "currency": "USD",
        "image_url": "https://example.com/img.jpg",
        "product_url": "https://fashionphile.com/products/123",
        "condition": "Shows Wear",
        "metadata": {"garment_type": "jewelry", "description": "Test desc"}
    }

@pytest.fixture
def firstdibs_raw():
    return {
        "product_id": "test-firstdibs-001",
        "brand": "Chanel",
        "model": "Chanel Belt",
        "price": 2617.6,
        "product_url": "https://1stdibs.com/fashion/belts/123",
        "full_description": "A beautiful belt",
        "main_images": [{"url": "https://example.com/img.jpg"}],
        "metadata": {
            "condition_display": "New",
            "availability": "In Stock"
        }
    }
