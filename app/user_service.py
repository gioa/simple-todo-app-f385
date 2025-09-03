"""Service layer for user management operations."""

from typing import List, Optional
from sqlmodel import select
from app.database import get_session
from app.models import User, UserCreate


class UserService:
    """Service class for user management operations."""

    @staticmethod
    def create_user(user_data: UserCreate) -> Optional[User]:
        """Create a new user."""
        with get_session() as session:
            # Check if email already exists
            existing_user = session.exec(select(User).where(User.email == user_data.email)).first()

            if existing_user is not None:
                return None

            user = User(name=user_data.name, email=user_data.email)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        with get_session() as session:
            return session.get(User, user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get a user by their email address."""
        with get_session() as session:
            return session.exec(select(User).where(User.email == email)).first()

    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users."""
        with get_session() as session:
            users = session.exec(select(User)).all()
            return list(users)

    @staticmethod
    def get_or_create_default_user() -> User:
        """Get the default user or create one if it doesn't exist."""
        default_email = "default@todo.app"

        user = UserService.get_user_by_email(default_email)
        if user is not None:
            return user

        user_data = UserCreate(name="Default User", email=default_email)
        created_user = UserService.create_user(user_data)

        # This should never be None since we checked for uniqueness above
        if created_user is None:
            raise RuntimeError("Failed to create default user")

        return created_user
