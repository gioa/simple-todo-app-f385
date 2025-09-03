"""Tests for user service functionality."""

import pytest
from app.database import reset_db
from app.user_service import UserService
from app.models import UserCreate


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_create_user_success(fresh_db):
    """Test successful user creation."""
    user_data = UserCreate(name="John Doe", email="john@example.com")
    user = UserService.create_user(user_data)

    assert user is not None
    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.is_active


def test_create_user_duplicate_email(fresh_db):
    """Test creating user with duplicate email fails."""
    user_data = UserCreate(name="John Doe", email="john@example.com")

    # Create first user
    user1 = UserService.create_user(user_data)
    assert user1 is not None

    # Try to create second user with same email
    user_data_2 = UserCreate(name="Jane Doe", email="john@example.com")
    user2 = UserService.create_user(user_data_2)
    assert user2 is None


def test_get_user_by_id_exists(fresh_db):
    """Test getting user by ID when user exists."""
    user_data = UserCreate(name="Test User", email="test@example.com")
    created_user = UserService.create_user(user_data)

    assert created_user is not None
    assert created_user.id is not None

    retrieved_user = UserService.get_user_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.name == "Test User"
    assert retrieved_user.email == "test@example.com"


def test_get_user_by_id_not_exists(fresh_db):
    """Test getting user by ID when user doesn't exist."""
    user = UserService.get_user_by_id(999)
    assert user is None


def test_get_user_by_email_exists(fresh_db):
    """Test getting user by email when user exists."""
    user_data = UserCreate(name="Email User", email="email@example.com")
    created_user = UserService.create_user(user_data)

    assert created_user is not None

    retrieved_user = UserService.get_user_by_email("email@example.com")

    assert retrieved_user is not None
    assert retrieved_user.name == "Email User"
    assert retrieved_user.email == "email@example.com"


def test_get_user_by_email_not_exists(fresh_db):
    """Test getting user by email when user doesn't exist."""
    user = UserService.get_user_by_email("nonexistent@example.com")
    assert user is None


def test_get_all_users_empty(fresh_db):
    """Test getting all users when database is empty."""
    users = UserService.get_all_users()
    assert users == []


def test_get_all_users_with_data(fresh_db):
    """Test getting all users when users exist."""
    user_data_1 = UserCreate(name="User 1", email="user1@example.com")
    user_data_2 = UserCreate(name="User 2", email="user2@example.com")

    user1 = UserService.create_user(user_data_1)
    user2 = UserService.create_user(user_data_2)

    assert user1 is not None
    assert user2 is not None

    users = UserService.get_all_users()

    assert len(users) == 2
    user_emails = {user.email for user in users}
    assert "user1@example.com" in user_emails
    assert "user2@example.com" in user_emails


def test_get_or_create_default_user_creates_new(fresh_db):
    """Test that get_or_create_default_user creates new user when none exists."""
    user = UserService.get_or_create_default_user()

    assert user is not None
    assert user.id is not None
    assert user.name == "Default User"
    assert user.email == "default@todo.app"


def test_get_or_create_default_user_returns_existing(fresh_db):
    """Test that get_or_create_default_user returns existing default user."""
    # Create default user
    first_call = UserService.get_or_create_default_user()
    assert first_call is not None
    assert first_call.id is not None

    # Second call should return the same user
    second_call = UserService.get_or_create_default_user()
    assert second_call is not None
    assert second_call.id == first_call.id
    assert second_call.name == first_call.name
    assert second_call.email == first_call.email


def test_user_email_uniqueness_constraint(fresh_db):
    """Test that email uniqueness is properly enforced."""
    # Create multiple users with different emails
    user1_data = UserCreate(name="User 1", email="unique1@example.com")
    user2_data = UserCreate(name="User 2", email="unique2@example.com")

    user1 = UserService.create_user(user1_data)
    user2 = UserService.create_user(user2_data)

    assert user1 is not None
    assert user2 is not None

    # Try to create user with existing email
    duplicate_data = UserCreate(name="Duplicate", email="unique1@example.com")
    duplicate_user = UserService.create_user(duplicate_data)

    assert duplicate_user is None

    # Verify original users still exist
    existing_user1 = UserService.get_user_by_email("unique1@example.com")
    existing_user2 = UserService.get_user_by_email("unique2@example.com")

    assert existing_user1 is not None
    assert existing_user1.name == "User 1"
    assert existing_user2 is not None
    assert existing_user2.name == "User 2"
