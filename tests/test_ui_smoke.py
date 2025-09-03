from nicegui.testing import User
from nicegui import ui
from typing import List, Dict
from logging import getLogger

logger = getLogger(__name__)

pytest_plugins = ["nicegui.testing.user_plugin"]


def extract_navigation_paths(element) -> List[str]:
    paths = []

    # Check for direct 'to' property (ui.link)
    if hasattr(element, "_props"):
        to_prop = element._props.get("to", "")
        if to_prop and to_prop.startswith("/"):
            paths.append(to_prop)

    return paths


def find_navigable_elements(user: User) -> Dict[str, List[str]]:
    """Find all potentially navigable elements and their target paths"""
    navigable = {"links": [], "buttons": [], "menu_items": []}

    # Find ui.link elements
    try:
        link_elements = user.find(ui.link).elements
        for link in link_elements:
            paths = extract_navigation_paths(link)
            navigable["links"].extend(paths)
    except AssertionError:
        logger.debug("No links found")

    # Find ui.button elements that might navigate
    try:
        button_elements = user.find(ui.button).elements
        for button in button_elements:
            # Check if button has navigation-related text
            button_text = getattr(button, "text", "").lower()
            nav_keywords = ["go to", "navigate", "open", "view", "show"]
            if any(keyword in button_text for keyword in nav_keywords):
                # This button might navigate, but we can't easily determine where
                # In a real test, we might need to click it and see what happens
                pass
    except AssertionError:
        logger.debug("No buttons found that might navigate")

    # Find ui.menu_item elements
    try:
        menu_elements = user.find(ui.menu_item).elements
        for menu_item in menu_elements:
            paths = extract_navigation_paths(menu_item)
            navigable["menu_items"].extend(paths)
    except AssertionError:
        logger.debug("No menu items found")

    return navigable


def test_app_startup():
    """Test that the app can start up without import errors."""
    # This is a basic smoke test that imports the main modules
    import app.startup
    import app.todo_app

    # Verify the functions exist
    assert callable(app.startup.startup)
    assert callable(app.todo_app.create)
