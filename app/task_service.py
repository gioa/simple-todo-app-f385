"""Service layer for task management operations."""

from datetime import datetime
from typing import List, Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import Task, TaskCreate, TaskUpdate, User


class TaskService:
    """Service class for task management operations."""

    @staticmethod
    def create_task(task_data: TaskCreate) -> Optional[Task]:
        """Create a new task."""
        with get_session() as session:
            # Verify user exists
            user = session.get(User, task_data.user_id)
            if user is None:
                return None

            task = Task(title=task_data.title, description=task_data.description, user_id=task_data.user_id)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def get_user_tasks(user_id: int, completed: Optional[bool] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by completion status."""
        with get_session() as session:
            query = select(Task).where(Task.user_id == user_id)

            if completed is not None:
                query = query.where(Task.completed == completed)

            query = query.order_by(desc(Task.created_at))
            tasks = session.exec(query).all()
            return list(tasks)

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        with get_session() as session:
            return session.get(Task, task_id)

    @staticmethod
    def update_task(task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None

            update_data = task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def toggle_task_completion(task_id: int) -> Optional[Task]:
        """Toggle the completion status of a task."""
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return None

            task.completed = not task.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """Delete a task by its ID."""
        with get_session() as session:
            task = session.get(Task, task_id)
            if task is None:
                return False

            session.delete(task)
            session.commit()
            return True
