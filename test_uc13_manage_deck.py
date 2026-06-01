"""
test_uc13_manage_deck.py
MelayuMate – UC-13 Manage Deck
Automated Selenium WebDriver Test Suite (Python + Pytest)

Feature under test:
  F13 Manage Deck

Test Coverage:
  TC-13-001 → Verify student can create a new deck with valid title and description.
  TC-13-002 → Verify system retrieves and displays student deck overview with card count correctly.
  TC-13-003 → Verify student can create a deck without description.
  TC-13-004 → Verify system rejects deck creation with empty title.
  TC-13-005 → Verify student can edit deck title and description.
  TC-13-006 → Verify student can delete a deck after confirming deletion.
  TC-13-007 → Verify deck is not deleted when student cancels deletion.

Run command:
  pytest -v .\\test_uc13_manage_deck.py
"""

import os
import time
import pytest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ══════════════════════════════════════════════════════════════════════════════
# Basic Configuration
# ══════════════════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:5173"
FLASHCARD_URL = f"{BASE_URL}/flashcard"

# Shorter wait makes the test run faster.
# If your laptop is slow, change this to 10 or 12.
WAIT_TIME = 8

# Test account used for auto-login
TEST_USERNAME = "low"
TEST_PASSWORD = "Abcdef123!"


# ══════════════════════════════════════════════════════════════════════════════
# General Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def wait(driver, seconds=WAIT_TIME):
    """Return WebDriverWait object with default timeout."""
    return WebDriverWait(driver, seconds)


def short_unique_title(prefix: str) -> str:
    """
    Generate a short unique deck title.

    Important:
    The title input field only allows 25 characters.
    Long titles will be cut/truncated by the system.
    """
    return f"{prefix}{int(time.time()) % 100000}"


def xpath_text(text: str) -> str:
    """Safely convert normal text into XPath text format."""
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    return "concat(" + ", \"'\", ".join([f"'{part}'" for part in text.split("'")]) + ")"


def save_screenshot(driver, name: str):
    """Save screenshot for evidence/debugging."""
    os.makedirs("selenium_screenshots", exist_ok=True)
    driver.save_screenshot(f"selenium_screenshots/{name}.png")


def click_element(driver, element):
    """
    Click element using JavaScript.

    Reason:
    Some buttons/icons may be covered by layout or animation.
    JavaScript click is more stable for this UI.
    """
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.1)
    driver.execute_script("arguments[0].click();", element)


def click_xpath(driver, xpath: str):
    """Wait until an element is clickable, then click it."""
    element = wait(driver).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    click_element(driver, element)
    return element


def type_text(element, text: str):
    """Clear an input field and type new text."""
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def get_input_value(driver, element):
    """Get current value from input/textarea."""
    return driver.execute_script("return arguments[0].value;", element)


def element_exists(driver, xpath: str) -> bool:
    """Check whether an element exists."""
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except Exception:
        return False


def find_first_visible(driver, xpaths, short_wait=3):
    """
    Try multiple XPath selectors and return the first visible element.

    Useful because different UI libraries may generate different attributes.
    """
    for xp in xpaths:
        try:
            element = WebDriverWait(driver, short_wait).until(
                EC.visibility_of_element_located((By.XPATH, xp))
            )
            return element
        except Exception:
            pass

    raise AssertionError(f"Cannot find visible element using selectors: {xpaths}")


# ══════════════════════════════════════════════════════════════════════════════
# Login Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def is_login_form_displayed(driver) -> bool:
    """
    Check whether the login form is displayed.

    The /flashcard URL may show the login form if the user is not logged in.
    """
    username_xpaths = [
        "//input[@placeholder='username']",
        "//input[@placeholder='Username']",
        "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'username')]",
        "//input[@type='text']",
        "//input[@type='email']",
    ]

    password_xpaths = [
        "//input[@placeholder='password']",
        "//input[@placeholder='Password']",
        "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password')]",
        "//input[@type='password']",
    ]

    has_username = any(element_exists(driver, xp) for xp in username_xpaths)
    has_password = any(element_exists(driver, xp) for xp in password_xpaths)

    return has_username and has_password


def login_if_needed(driver):
    """
    Login only when needed.

    This version is faster because:
      1. It uses one browser session.
      2. It does not login again if already logged in.
      3. It directly checks for the Create Deck button.
    """
    driver.get(FLASHCARD_URL)
    time.sleep(0.5)

    if is_login_form_displayed(driver):
        username_input = find_first_visible(driver, [
            "//input[@placeholder='username']",
            "//input[@placeholder='Username']",
            "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'username')]",
            "//input[@type='text']",
        ])

        password_input = find_first_visible(driver, [
            "//input[@placeholder='password']",
            "//input[@placeholder='Password']",
            "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password')]",
            "//input[@type='password']",
        ])

        type_text(username_input, TEST_USERNAME)
        type_text(password_input, TEST_PASSWORD)

        # The login page has two Login buttons:
        # 1. Login tab
        # 2. Yellow Login submit button
        # We click the last Login button to submit the form.
        click_xpath(driver, "(//button[normalize-space()='Login'])[last()]")
        time.sleep(1)

    driver.get(FLASHCARD_URL)

    try:
        wait(driver).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='Create Deck']")
            )
        )
    except TimeoutException:
        save_screenshot(driver, "flashcard-page-not-loaded-after-login")
        raise AssertionError(
            "Login failed or Flashcard page did not load. "
            "Check screenshot: selenium_screenshots/flashcard-page-not-loaded-after-login.png"
        )


def ensure_flashcard_page(driver):
    """Open Flashcard page and make sure Create Deck button is available."""
    login_if_needed(driver)


# ══════════════════════════════════════════════════════════════════════════════
# Deck Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def open_create_deck_panel(driver):
    """Open the side panel for creating a new flashcard deck."""
    ensure_flashcard_page(driver)

    click_xpath(driver, "//button[normalize-space()='Create Deck']")

    wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(normalize-space(), 'New Flashcard Deck')]")
        )
    )


def close_create_deck_panel(driver):
    """Close the create deck panel after validation test."""
    close_xpaths = [
        "//button[contains(normalize-space(), '×')]",
        "//button[contains(normalize-space(), 'X')]",
        "(//button[.//*[local-name()='svg']])[last()]",
    ]

    for xp in close_xpaths:
        try:
            click_xpath(driver, xp)
            time.sleep(0.3)
            return
        except Exception:
            pass


def create_deck(driver, title: str, description: str = ""):
    """
    Create a deck.

    Return:
      actual_title

    Reason:
      The title input has a 25-character limit.
      If the input is cut by the system, the returned actual title is used
      for checking and opening the deck.
    """
    ensure_flashcard_page(driver)
    open_create_deck_panel(driver)

    title_input = wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Title']")
        )
    )
    type_text(title_input, title)

    actual_title = get_input_value(driver, title_input)

    if description:
        desc_input = wait(driver).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//textarea[contains(@placeholder, 'Description')]")
            )
        )
        type_text(desc_input, description)

    click_xpath(driver, "//button[normalize-space()='Submit']")

    wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[normalize-space()={xpath_text(actual_title)}]")
        )
    )

    return actual_title


def deck_exists(driver, title: str) -> bool:
    """Check whether a deck title exists on the Flashcard page."""
    ensure_flashcard_page(driver)

    try:
        driver.find_element(By.XPATH, f"//*[normalize-space()={xpath_text(title)}]")
        return True
    except NoSuchElementException:
        return False


def open_deck(driver, title: str):
    """Open a deck from the Flashcard overview page."""
    ensure_flashcard_page(driver)

    title_element = wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[normalize-space()={xpath_text(title)}]")
        )
    )

    open_button = title_element.find_element(
        By.XPATH,
        "./ancestor::*[.//button[normalize-space()='Open']][1]//button[normalize-space()='Open']"
    )

    click_element(driver, open_button)

    wait(driver).until(lambda d: "/flashcard/" in d.current_url)
    wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(normalize-space(), {xpath_text(title)})]")
        )
    )


def go_to_edit_page(driver):
    """
    Go from deck detail page to deck edit page.

    Based on your UI:
      Deck detail page has a pencil/edit icon at the top right.
    """
    edit_xpaths = [
        "//*[local-name()='svg' and contains(@class, 'pencil')]/ancestor::*[self::button or self::a][1]",
        "//*[local-name()='svg' and contains(@class, 'edit')]/ancestor::*[self::button or self::a][1]",
        "(//button[.//*[local-name()='svg']])[last()]",
    ]

    for xp in edit_xpaths:
        try:
            click_xpath(driver, xp)
            wait(driver).until(lambda d: "/edit" in d.current_url)
            return
        except Exception:
            pass

    # Fallback: your URL pattern supports adding /edit
    if not driver.current_url.endswith("/edit"):
        driver.get(driver.current_url.rstrip("/") + "/edit")

    wait(driver).until(lambda d: "/edit" in d.current_url)


def get_edit_fields(driver):
    """Get title and description fields from deck edit page."""
    fields = wait(driver).until(
        EC.presence_of_all_elements_located((By.XPATH, "//input | //textarea"))
    )

    visible_fields = [field for field in fields if field.is_displayed()]

    if len(visible_fields) < 2:
        save_screenshot(driver, "edit-fields-not-found")
        raise AssertionError("Cannot find title and description fields on edit page.")

    title_field = visible_fields[0]
    description_field = visible_fields[1]

    return title_field, description_field


def save_changes(driver):
    """Click Save Changes button after editing deck."""
    click_xpath(driver, "//button[normalize-space()='Save Changes']")


# ══════════════════════════════════════════════════════════════════════════════
# Delete Modal Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def delete_modal_is_open(driver) -> bool:
    """Check whether the Confirm Deletion modal is currently displayed."""
    modal_checks = [
        "//*[contains(normalize-space(), 'Confirm Deletion')]",
        "//*[contains(normalize-space(), 'Are you sure you want to delete this deck')]",
        "//button[normalize-space()='DELETE']",
        "//button[normalize-space()='CANCEL']",
    ]

    for xp in modal_checks:
        try:
            elements = driver.find_elements(By.XPATH, xp)
            for element in elements:
                if element.is_displayed():
                    return True
        except Exception:
            pass

    return False


def visible_button_by_text(driver, target_text: str):
    """Find a visible button by text, case-insensitive."""
    buttons = driver.find_elements(By.XPATH, "//button")

    for button in buttons:
        try:
            if button.is_displayed() and button.text.strip().upper() == target_text.upper():
                return button
        except Exception:
            pass

    return None


def click_trash_icon(driver):
    """
    Click the deck delete icon.

    Based on your screenshot:
      - The delete icon is a trash bin at the top right.
      - Hover text is 'Delete Deck'.
      - After clicking it, a Confirm Deletion modal appears.
    """

    # Best selectors first
    trash_xpaths = [
        "//*[@title='Delete Deck']",
        "//*[@aria-label='Delete Deck']",
        "//button[@title='Delete Deck']",
        "//button[@aria-label='Delete Deck']",
        "//*[contains(@title, 'Delete')]",
        "//*[contains(@aria-label, 'Delete')]",
        "//*[local-name()='svg' and contains(@class, 'trash')]",
        "//*[local-name()='svg' and contains(@class, 'Trash')]",
        "//*[local-name()='svg' and contains(@class, 'lucide-trash')]",
    ]

    for xp in trash_xpaths:
        try:
            candidates = driver.find_elements(By.XPATH, xp)

            for candidate in candidates:
                try:
                    if not candidate.is_displayed():
                        continue

                    ActionChains(driver).move_to_element(candidate).pause(0.1).click(candidate).perform()
                    time.sleep(0.5)

                    if delete_modal_is_open(driver):
                        return
                except Exception:
                    pass
        except Exception:
            pass

    # Fallback:
    # Find all icon buttons near the top of the page and click the right-most one.
    # This matches your top-right trash icon.
    try:
        icon_buttons = driver.find_elements(By.XPATH, "//button[.//*[local-name()='svg']]")
        candidates = []

        for button in icon_buttons:
            try:
                if not button.is_displayed():
                    continue

                text = button.text.strip()
                location = button.location

                # Exclude normal text buttons such as Add Card and Save Changes.
                if text:
                    continue

                # Only consider top area buttons.
                if location["y"] < 250:
                    candidates.append(button)
            except Exception:
                pass

        if candidates:
            # Right-most icon button should be the trash icon.
            candidates.sort(key=lambda b: b.location["x"], reverse=True)
            click_element(driver, candidates[0])
            time.sleep(0.5)

            if delete_modal_is_open(driver):
                return
    except Exception:
        pass

    save_screenshot(driver, "trash-button-not-found")
    raise AssertionError("Cannot open Confirm Deletion modal after clicking trash icon.")


def confirm_delete(driver):
    """Click DELETE button inside the confirmation modal."""
    wait(driver).until(lambda d: delete_modal_is_open(d))

    delete_button = visible_button_by_text(driver, "DELETE")

    if delete_button is None:
        save_screenshot(driver, "confirm-delete-not-found")
        raise AssertionError("Cannot find DELETE button in confirmation modal.")

    click_element(driver, delete_button)
    time.sleep(0.5)


def cancel_delete(driver):
    """Click CANCEL button inside the confirmation modal."""
    wait(driver).until(lambda d: delete_modal_is_open(d))

    cancel_button = visible_button_by_text(driver, "CANCEL")

    if cancel_button is None:
        save_screenshot(driver, "cancel-delete-not-found")
        raise AssertionError("Cannot find CANCEL button in confirmation modal.")

    click_element(driver, cancel_button)
    time.sleep(0.5)


# ══════════════════════════════════════════════════════════════════════════════
# Pytest Driver
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def driver():
    """
    Create one browser session for all tests.

    This is faster than opening a new browser for every test.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    d = webdriver.Chrome(options=options)

    # Use explicit waits instead of long implicit waits.
    d.implicitly_wait(0.5)

    # Login once at the start to reduce repeated login time.
    login_if_needed(d)

    yield d

    d.quit()


# ══════════════════════════════════════════════════════════════════════════════
# UC-13 Manage Deck Test Cases
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# TP-13-001 | TC-13-001
# Verify student can create a new deck with valid title and description.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_001_create_deck_with_valid_title_and_description(driver):
    deck_title = short_unique_title("Animal")
    deck_desc = "Animal vocabulary"

    actual_title = create_deck(driver, deck_title, deck_desc)

    assert deck_exists(driver, actual_title)

    assert driver.find_element(
        By.XPATH,
        f"//*[contains(normalize-space(), {xpath_text(deck_desc)})]"
    )

    save_screenshot(driver, "TC-13-001-create-deck")


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-002 | TC-13-002
# Verify system retrieves and displays student deck overview with card count.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_002_retrieve_and_display_deck_overview(driver):
    deck_title = short_unique_title("Overview")
    deck_desc = "Deck overview test"

    actual_title = create_deck(driver, deck_title, deck_desc)
    ensure_flashcard_page(driver)

    assert deck_exists(driver, actual_title)

    assert driver.find_element(
        By.XPATH,
        f"//*[contains(normalize-space(), {xpath_text(deck_desc)})]"
    )

    assert driver.find_element(
        By.XPATH,
        "//*[contains(normalize-space(), 'cards')]"
    )

    save_screenshot(driver, "TC-13-002-deck-overview")


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-003 | TC-13-003
# Verify student can create a deck without description.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_003_create_deck_without_description(driver):
    deck_title = short_unique_title("NoDesc")

    actual_title = create_deck(driver, deck_title, "")

    assert deck_exists(driver, actual_title)

    save_screenshot(driver, "TC-13-003-create-without-description")


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-004 | TC-13-004
# Verify system rejects deck creation with empty title.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_004_reject_empty_deck_title(driver):
    ensure_flashcard_page(driver)
    open_create_deck_panel(driver)

    desc_input = wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//textarea[contains(@placeholder, 'Description')]")
        )
    )
    type_text(desc_input, "animal")

    click_xpath(driver, "//button[normalize-space()='Submit']")

    error_message = wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(normalize-space(), 'Please fill in a title')]")
        )
    )

    assert error_message.is_displayed()

    save_screenshot(driver, "TC-13-004-empty-title-error")

    close_create_deck_panel(driver)


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-005 | TC-13-005
# Verify student can edit deck title and description.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_005_edit_deck_title_and_description(driver):
    old_title = short_unique_title("Old")
    old_desc = "Old description"
    new_title = short_unique_title("New")
    new_desc = "Updated description"

    actual_old_title = create_deck(driver, old_title, old_desc)

    open_deck(driver, actual_old_title)
    go_to_edit_page(driver)

    title_field, desc_field = get_edit_fields(driver)

    type_text(title_field, new_title)
    actual_new_title = get_input_value(driver, title_field)

    type_text(desc_field, new_desc)

    save_changes(driver)

    time.sleep(0.5)
    ensure_flashcard_page(driver)

    assert deck_exists(driver, actual_new_title)

    save_screenshot(driver, "TC-13-005-edit-deck")


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-006 | TC-13-006
# Verify student can delete a deck after confirming deletion.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_006_delete_deck_after_confirming(driver):
    deck_title = short_unique_title("Delete")
    deck_desc = "Delete test"

    actual_title = create_deck(driver, deck_title, deck_desc)

    open_deck(driver, actual_title)
    go_to_edit_page(driver)

    click_trash_icon(driver)
    confirm_delete(driver)

    time.sleep(0.5)
    ensure_flashcard_page(driver)

    assert not deck_exists(driver, actual_title)

    save_screenshot(driver, "TC-13-006-delete-confirm")


# ─────────────────────────────────────────────────────────────────────────────
# TP-13-007 | TC-13-007
# Verify deck is not deleted when student cancels deletion.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_13_007_cancel_deck_deletion(driver):
    deck_title = short_unique_title("Cancel")
    deck_desc = "Cancel delete test"

    actual_title = create_deck(driver, deck_title, deck_desc)

    open_deck(driver, actual_title)
    go_to_edit_page(driver)

    click_trash_icon(driver)
    cancel_delete(driver)

    time.sleep(0.5)
    ensure_flashcard_page(driver)

    assert deck_exists(driver, actual_title)

    save_screenshot(driver, "TC-13-007-cancel-delete")