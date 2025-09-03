"""Tests for task service functionality."""

import pytest
from datetime import datetime
from app.database import reset_db
from app.task_service import TaskService
from app.user_service import UserService
from app.models import TaskCreate, TaskUpdate, UserCreate


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test."""
    reset_db()
    yield
    reset_db()


@pytest.fixture()
def sample_user():
    """Create a sample user for testing."""
    user_data = UserCreate(name="Test User", email="test@example.com")
    user = UserService.create_user(user_data)
    assert user is not None
    assert user.id is not None
    return user


def test_create_task_success(fresh_db, sample_user):
    """Test successful task creation."""
    task_data = TaskCreate(title="Complete project", description="Finish the todo application", user_id=sample_user.id)

    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None
    assert task.title == "Complete project"
    assert task.description == "Finish the todo application"
    assert task.user_id == sample_user.id
    assert not task.completed
    assert isinstance(task.created_at, datetime)


def test_create_task_nonexistent_user(fresh_db):
    """Test task creation with non-existent user."""
    task_data = TaskCreate(title="Test task", description="This should fail", user_id=999)

    task = TaskService.create_task(task_data)
    assert task is None


def test_get_user_tasks_empty(fresh_db, sample_user):
    """Test getting tasks when user has none."""
    tasks = TaskService.get_user_tasks(sample_user.id)
    assert tasks == []


def test_get_user_tasks_with_data(fresh_db, sample_user):
    """Test getting tasks when user has tasks."""
    # Create multiple tasks
    task_data_1 = TaskCreate(title="Task 1", user_id=sample_user.id)
    task_data_2 = TaskCreate(title="Task 2", user_id=sample_user.id)

    task1 = TaskService.create_task(task_data_1)
    task2 = TaskService.create_task(task_data_2)

    assert task1 is not None
    assert task2 is not None

    tasks = TaskService.get_user_tasks(sample_user.id)

    assert len(tasks) == 2
    # Should be ordered by created_at desc
    assert tasks[0].title == "Task 2"
    assert tasks[1].title == "Task 1"


def test_get_user_tasks_filtered_by_completion(fresh_db, sample_user):
    """Test getting tasks filtered by completion status."""
    # Create tasks and complete one
    task_data_1 = TaskCreate(title="Active Task", user_id=sample_user.id)
    task_data_2 = TaskCreate(title="Completed Task", user_id=sample_user.id)

    task1 = TaskService.create_task(task_data_1)
    task2 = TaskService.create_task(task_data_2)

    assert task1 is not None
    assert task2 is not None
    assert task2.id is not None

    # Mark task2 as completed
    TaskService.toggle_task_completion(task2.id)

    # Test filtering
    active_tasks = TaskService.get_user_tasks(sample_user.id, completed=False)
    completed_tasks = TaskService.get_user_tasks(sample_user.id, completed=True)
    all_tasks = TaskService.get_user_tasks(sample_user.id)

    assert len(active_tasks) == 1
    assert active_tasks[0].title == "Active Task"
    assert not active_tasks[0].completed

    assert len(completed_tasks) == 1
    assert completed_tasks[0].title == "Completed Task"
    assert completed_tasks[0].completed

    assert len(all_tasks) == 2


def test_get_task_by_id_exists(fresh_db, sample_user):
    """Test getting a task by ID when it exists."""
    task_data = TaskCreate(title="Test Task", user_id=sample_user.id)
    created_task = TaskService.create_task(task_data)

    assert created_task is not None
    assert created_task.id is not None

    retrieved_task = TaskService.get_task_by_id(created_task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == "Test Task"


def test_get_task_by_id_not_exists(fresh_db):
    """Test getting a task by ID when it doesn't exist."""
    task = TaskService.get_task_by_id(999)
    assert task is None


def test_update_task_success(fresh_db, sample_user):
    """Test successful task update."""
    task_data = TaskCreate(title="Original Title", description="Original Description", user_id=sample_user.id)
    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None

    update_data = TaskUpdate(title="Updated Title", description="Updated Description")
    updated_task = TaskService.update_task(task.id, update_data)

    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"
    assert updated_task.updated_at is not None


def test_update_task_partial(fresh_db, sample_user):
    """Test partial task update."""
    task_data = TaskCreate(title="Original Title", description="Original Description", user_id=sample_user.id)
    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None

    # Update only title
    update_data = TaskUpdate(title="New Title")
    updated_task = TaskService.update_task(task.id, update_data)

    assert updated_task is not None
    assert updated_task.title == "New Title"
    assert updated_task.description == "Original Description"  # Should remain unchanged


def test_update_task_not_exists(fresh_db):
    """Test updating a task that doesn't exist."""
    update_data = TaskUpdate(title="New Title")
    result = TaskService.update_task(999, update_data)
    assert result is None


def test_toggle_task_completion_success(fresh_db, sample_user):
    """Test successful task completion toggle."""
    task_data = TaskCreate(title="Test Task", user_id=sample_user.id)
    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None
    assert not task.completed

    # Toggle to completed
    updated_task = TaskService.toggle_task_completion(task.id)
    assert updated_task is not None
    assert updated_task.completed
    assert updated_task.updated_at is not None

    # Toggle back to incomplete
    updated_task = TaskService.toggle_task_completion(task.id)
    assert updated_task is not None
    assert not updated_task.completed


def test_toggle_task_completion_not_exists(fresh_db):
    """Test toggling completion for non-existent task."""
    result = TaskService.toggle_task_completion(999)
    assert result is None


def test_delete_task_success(fresh_db, sample_user):
    """Test successful task deletion."""
    task_data = TaskCreate(title="To Delete", user_id=sample_user.id)
    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None

    # Verify task exists
    retrieved_task = TaskService.get_task_by_id(task.id)
    assert retrieved_task is not None

    # Delete task
    success = TaskService.delete_task(task.id)
    assert success

    # Verify task no longer exists
    deleted_task = TaskService.get_task_by_id(task.id)
    assert deleted_task is None


def test_delete_task_not_exists(fresh_db):
    """Test deleting a task that doesn't exist."""
    success = TaskService.delete_task(999)
    assert not success


def test_multiple_users_tasks_isolation(fresh_db):
    """Test that tasks are properly isolated between users."""
    # Create two users
    user1_data = UserCreate(name="User 1", email="user1@example.com")
    user2_data = UserCreate(name="User 2", email="user2@example.com")

    user1 = UserService.create_user(user1_data)
    user2 = UserService.create_user(user2_data)

    assert user1 is not None
    assert user2 is not None
    assert user1.id is not None
    assert user2.id is not None

    # Create tasks for each user
    task1_data = TaskCreate(title="User 1 Task", user_id=user1.id)
    task2_data = TaskCreate(title="User 2 Task", user_id=user2.id)

    TaskService.create_task(task1_data)
    TaskService.create_task(task2_data)

    # Verify task isolation
    user1_tasks = TaskService.get_user_tasks(user1.id)
    user2_tasks = TaskService.get_user_tasks(user2.id)

    assert len(user1_tasks) == 1
    assert len(user2_tasks) == 1
    assert user1_tasks[0].title == "User 1 Task"
    assert user2_tasks[0].title == "User 2 Task"


def test_task_timestamps(fresh_db, sample_user):
    """Test that task timestamps are handled correctly."""
    task_data = TaskCreate(title="Timestamp Test", user_id=sample_user.id)
    task = TaskService.create_task(task_data)

    assert task is not None
    assert task.id is not None
    assert isinstance(task.created_at, datetime)
    assert task.updated_at is None

    # Update task and check updated_at
    update_data = TaskUpdate(title="Updated Title")
    updated_task = TaskService.update_task(task.id, update_data)

    assert updated_task is not None
    assert updated_task.updated_at is not None
    assert updated_task.updated_at > updated_task.created_at
