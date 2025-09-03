"""Todo application UI components and pages."""

import logging
from nicegui import ui
from typing import Optional, Callable
from app.task_service import TaskService
from app.user_service import UserService
from app.models import Task, TaskCreate

logger = logging.getLogger(__name__)


def apply_modern_theme():
    """Apply modern color theme to the application."""
    ui.colors(
        primary="#2563eb",  # Professional blue
        secondary="#64748b",  # Subtle gray
        accent="#10b981",  # Success green
        positive="#10b981",
        negative="#ef4444",  # Error red
        warning="#f59e0b",  # Warning amber
        info="#3b82f6",  # Info blue
    )


class TextStyles:
    """Reusable text styles for consistency."""

    HEADING = "text-2xl font-bold text-gray-800 mb-4"
    SUBHEADING = "text-lg font-semibold text-gray-700 mb-2"
    BODY = "text-base text-gray-600 leading-relaxed"
    CAPTION = "text-sm text-gray-500"


def create_task_card(task: Task, on_toggle: Callable[[int], None], on_delete: Callable[[int], None]) -> None:
    """Create a modern task card component."""
    card_classes = "bg-white shadow-md rounded-lg p-4 mb-3 hover:shadow-lg transition-shadow"

    if task.completed:
        card_classes += " bg-green-50 border-l-4 border-green-400"

    with ui.card().classes(card_classes):
        with ui.row().classes("w-full items-start justify-between"):
            with ui.column().classes("flex-1 min-w-0"):
                title_classes = "text-lg font-semibold"
                if task.completed:
                    title_classes += " line-through text-gray-500"
                else:
                    title_classes += " text-gray-800"

                ui.label(task.title).classes(title_classes)

                if task.description:
                    desc_classes = "text-sm mt-1"
                    if task.completed:
                        desc_classes += " text-gray-400"
                    else:
                        desc_classes += " text-gray-600"
                    ui.label(task.description).classes(desc_classes)

                # Task metadata
                created_date = task.created_at.strftime("%b %d, %Y at %I:%M %p")
                ui.label(f"Created: {created_date}").classes("text-xs text-gray-400 mt-2")

                if task.updated_at:
                    updated_date = task.updated_at.strftime("%b %d, %Y at %I:%M %p")
                    ui.label(f"Updated: {updated_date}").classes("text-xs text-gray-400")

            with ui.column().classes("flex-none ml-4"):
                # Toggle completion button
                toggle_icon = "check_circle" if task.completed else "radio_button_unchecked"
                toggle_color = "positive" if task.completed else "grey-5"

                if task.id is not None:
                    task_id = task.id  # Capture the ID to avoid closure issues
                    ui.button(icon=toggle_icon, on_click=lambda _=None, t_id=task_id: on_toggle(t_id)).props(
                        f"flat round color={toggle_color}"
                    ).classes("mb-2")

                    # Delete button
                    ui.button(icon="delete", on_click=lambda _=None, t_id=task_id: on_delete(t_id)).props(
                        "flat round color=negative"
                    )


def create():
    """Create the todo application routes and UI."""
    apply_modern_theme()

    @ui.page("/")
    def todo_page():
        # Ensure we have a default user
        user = UserService.get_or_create_default_user()
        if user.id is None:
            ui.notify("Error: Could not initialize user", type="negative")
            return

        # Page header
        with ui.column().classes("w-full max-w-4xl mx-auto p-6"):
            ui.label("📝 Todo Application").classes("text-3xl font-bold text-primary mb-2")
            ui.label("Organize your tasks efficiently").classes(TextStyles.BODY + " mb-6")

            # Task creation form
            with ui.card().classes("w-full p-6 mb-6 shadow-lg rounded-xl"):
                ui.label("Add New Task").classes(TextStyles.SUBHEADING)

                with ui.row().classes("w-full gap-4 items-end"):
                    task_title = (
                        ui.input(label="Task Title", placeholder="What needs to be done?")
                        .classes("flex-1")
                        .props("outlined")
                    )

                    task_description = (
                        ui.textarea(label="Description (optional)", placeholder="Add more details...")
                        .classes("flex-1")
                        .props("outlined rows=2")
                    )

                    ui.button("Add Task", icon="add", on_click=lambda: add_task()).classes(
                        "bg-primary text-white px-6 py-3 h-fit"
                    )

            # Task filters
            with ui.row().classes("gap-4 mb-4"):
                ui.button("All Tasks", on_click=lambda: show_tasks()).classes("px-4 py-2").props("outline")
                ui.button("Active", on_click=lambda: show_tasks(completed=False)).classes("px-4 py-2").props("outline")
                ui.button("Completed", on_click=lambda: show_tasks(completed=True)).classes("px-4 py-2").props(
                    "outline"
                )

            # Tasks container
            tasks_container = ui.column().classes("w-full")

            # Task statistics
            stats_container = ui.row().classes("gap-4 mt-6")

        def add_task():
            """Add a new task."""
            title = task_title.value.strip()
            description = task_description.value.strip()

            if not title:
                ui.notify("Task title is required", type="warning")
                return

            if user.id is None:
                ui.notify("User not properly initialized", type="negative")
                return

            try:
                task_data = TaskCreate(title=title, description=description, user_id=user.id)

                created_task = TaskService.create_task(task_data)
                if created_task is None:
                    ui.notify("Failed to create task", type="negative")
                    return

                # Clear form
                task_title.value = ""
                task_description.value = ""

                ui.notify("Task added successfully!", type="positive")
                show_tasks()  # Refresh task list

            except Exception as e:
                logger.error(f"Error creating task: {str(e)}")
                ui.notify(f"Error creating task: {str(e)}", type="negative")

        def toggle_task(task_id: int):
            """Toggle task completion status."""
            try:
                updated_task = TaskService.toggle_task_completion(task_id)
                if updated_task is None:
                    ui.notify("Task not found", type="warning")
                    return

                status = "completed" if updated_task.completed else "marked as active"
                ui.notify(f"Task {status}", type="positive")
                show_tasks()  # Refresh task list

            except Exception as e:
                logger.error(f"Error updating task: {str(e)}")
                ui.notify(f"Error updating task: {str(e)}", type="negative")

        def delete_task(task_id: int):
            """Delete a task."""
            try:
                success = TaskService.delete_task(task_id)
                if not success:
                    ui.notify("Task not found", type="warning")
                    return

                ui.notify("Task deleted", type="info")
                show_tasks()  # Refresh task list

            except Exception as e:
                logger.error(f"Error deleting task: {str(e)}")
                ui.notify(f"Error deleting task: {str(e)}", type="negative")

        def show_tasks(completed: Optional[bool] = None):
            """Display tasks with optional completion filter."""
            if user.id is None:
                ui.notify("User not properly initialized", type="negative")
                return

            try:
                tasks = TaskService.get_user_tasks(user.id, completed=completed)

                # Clear and update tasks container
                tasks_container.clear()

                if not tasks:
                    with tasks_container:
                        with ui.card().classes("w-full p-8 text-center bg-gray-50"):
                            ui.icon("task_alt", size="3em").classes("text-gray-300 mb-4")
                            ui.label("No tasks found").classes("text-xl text-gray-500 mb-2")
                            filter_text = {
                                None: "Create your first task to get started!",
                                False: "All tasks are completed! Great job! 🎉",
                                True: "No completed tasks yet.",
                            }[completed]
                            ui.label(filter_text).classes("text-gray-400")
                else:
                    with tasks_container:
                        for task in tasks:
                            create_task_card(task, toggle_task, delete_task)

                # Update statistics
                update_statistics()

            except Exception as e:
                logger.error(f"Error loading tasks: {str(e)}")
                ui.notify(f"Error loading tasks: {str(e)}", type="negative")

        def update_statistics():
            """Update task statistics display."""
            if user.id is None:
                ui.notify("User not properly initialized", type="negative")
                return

            try:
                all_tasks = TaskService.get_user_tasks(user.id)
                completed_tasks = TaskService.get_user_tasks(user.id, completed=True)
                active_tasks = TaskService.get_user_tasks(user.id, completed=False)

                stats_container.clear()

                with stats_container:
                    # Total tasks
                    with ui.card().classes("p-4 bg-blue-50 border border-blue-200 rounded-lg"):
                        ui.label(str(len(all_tasks))).classes("text-2xl font-bold text-blue-600")
                        ui.label("Total Tasks").classes("text-sm text-blue-500 uppercase tracking-wider")

                    # Active tasks
                    with ui.card().classes("p-4 bg-orange-50 border border-orange-200 rounded-lg"):
                        ui.label(str(len(active_tasks))).classes("text-2xl font-bold text-orange-600")
                        ui.label("Active").classes("text-sm text-orange-500 uppercase tracking-wider")

                    # Completed tasks
                    with ui.card().classes("p-4 bg-green-50 border border-green-200 rounded-lg"):
                        ui.label(str(len(completed_tasks))).classes("text-2xl font-bold text-green-600")
                        ui.label("Completed").classes("text-sm text-green-500 uppercase tracking-wider")

            except Exception as e:
                logger.error(f"Error updating statistics: {str(e)}")
                ui.notify(f"Error updating statistics: {str(e)}", type="negative")

        # Initial load
        show_tasks()
