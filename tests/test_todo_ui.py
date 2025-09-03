"""Basic smoke test for todo application UI."""

import pytest
from app.database import reset_db


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


def test_todo_app_imports_successfully(fresh_db):
    """Test that the todo application can be imported without errors."""
    import app.todo_app

    # Test that the module has the expected functions
    assert hasattr(app.todo_app, "create")
    assert hasattr(app.todo_app, "apply_modern_theme")
    assert hasattr(app.todo_app, "TextStyles")
    assert hasattr(app.todo_app, "create_task_card")


def test_todo_app_create_function_exists(fresh_db):
    """Test that the create function exists and is callable."""
    import app.todo_app

    # Should be able to call create function without errors
    # This tests the module structure but doesn't test UI interaction
    assert callable(app.todo_app.create)
