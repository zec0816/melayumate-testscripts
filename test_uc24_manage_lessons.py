import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Base URL
BASE_URL = "http://localhost:5173"

# Lecturer credentials
LECTURER_USERNAME = "lecturer01"
LECTURER_PASSWORD = "Lecturer123@"


# =========================================================
# DRIVER SETUP
# =========================================================
@pytest.fixture
def driver():

    # Launch Chrome browser
    driver = webdriver.Chrome()

    # Maximize browser window
    driver.maximize_window()

    yield driver

    # Close browser after test
    driver.quit()


# =========================================================
# LOGIN FUNCTION
# =========================================================
def lecturer_login(driver):

    wait = WebDriverWait(driver, 10)

    # Open login page
    driver.get(BASE_URL)

    # Enter username
    username_input = wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    username_input.clear()
    username_input.send_keys(LECTURER_USERNAME)

    # Enter password
    password_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Password']")
        )
    )

    password_input.clear()
    password_input.send_keys(LECTURER_PASSWORD)

    # Click Sign In button
    sign_in_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Sign In')]")
        )
    )

    sign_in_btn.click()

    # Wait until dashboard loaded
    wait.until(EC.url_contains("/dashboard"))

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Lecturer Dashboard')]")
        )
    )


# =========================================================
# OPEN ADD LESSON FORM
# =========================================================
def click_add_lesson(driver):

    wait = WebDriverWait(driver, 10)

    # Locate add lesson button
    add_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'bg-purple')]")
        )
    )

    # Click add button
    driver.execute_script("arguments[0].click();", add_btn)

    # Wait for sliding form animation
    time.sleep(1)


# =========================================================
# FILL LESSON FORM
# =========================================================
def fill_lesson_form(driver, title=None, description=None):

    wait = WebDriverWait(driver, 10)

    # Enter title
    if title is not None:

        title_input = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@placeholder='Title']")
            )
        )

        title_input.clear()
        title_input.send_keys(title)

    # Enter description
    if description is not None:

        desc_input = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//textarea[contains(@placeholder,'Description')]")
            )
        )

        desc_input.clear()
        desc_input.send_keys(description)


# =========================================================
# SUBMIT LESSON FORM
# =========================================================
def submit_lesson_form(driver):

    wait = WebDriverWait(driver, 10)

    # Locate submit button
    submit_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Submit')]")
        )
    )

    # Click submit
    driver.execute_script(
        "arguments[0].click();",
        submit_btn
    )

    time.sleep(1)


# =========================================================
# CREATE LESSON
# =========================================================
def create_lesson(driver, title, description=None):

    # Open add lesson form
    click_add_lesson(driver)

    # Fill lesson details
    fill_lesson_form(
        driver,
        title=title,
        description=description
    )

    # Submit lesson
    submit_lesson_form(driver)

    wait = WebDriverWait(driver, 10)

    # Wait until lesson appears
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[contains(text(),'{title}')]")
        )
    )


# =========================================================
# CHECK LESSON EXISTENCE
# =========================================================
def lesson_exists(driver, lesson_title):

    # Find lesson by title
    lessons = driver.find_elements(
        By.XPATH,
        f"//*[contains(text(),'{lesson_title}')]"
    )

    return len(lessons) > 0


# =========================================================
# GET LESSON CARD
# =========================================================
def get_lesson_card(driver, lesson_title):

    wait = WebDriverWait(driver, 10)

    # Locate lesson card container
    lesson_card = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//*[contains(text(),'{lesson_title}')]/ancestor::div[contains(@class,'rounded')]"
            )
        )
    )

    return lesson_card


# =========================================================
# CLICK TRASH BUTTON
# =========================================================
def click_lesson_trash(driver, lesson_title):

    wait = WebDriverWait(driver, 10)

    # Get lesson card
    lesson_card = get_lesson_card(driver, lesson_title)

    # Scroll lesson card into view
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        lesson_card
    )

    # Locate trash button
    trash_btn = lesson_card.find_element(
        By.XPATH,
        ".//button[@title='Delete Lesson']"
    )

    # Click trash button
    driver.execute_script(
        "arguments[0].click();",
        trash_btn
    )

    # Wait for delete dialog
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//*[contains(text(),'Confirm Lesson Deletion')]"
            )
        )
    )


# =========================================================
# CLICK DELETE BUTTON IN DIALOG
# =========================================================
def click_delete_in_dialog(driver):

    wait = WebDriverWait(driver, 10)

    # Wait for dialog
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(),'Confirm Lesson Deletion')]")
        )
    )

    # Get all visible buttons
    buttons = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//button")
        )
    )

    visible_buttons = [btn for btn in buttons if btn.is_displayed()]

    # Last visible button = DELETE
    delete_btn = visible_buttons[-1]

    # Scroll to delete button
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        delete_btn
    )

    # Click delete button
    ActionChains(driver).move_to_element(delete_btn).click().perform()

    time.sleep(1)


# =========================================================
# CLICK CANCEL BUTTON IN DIALOG
# =========================================================
def click_cancel_in_dialog(driver):

    wait = WebDriverWait(driver, 10)

    # Wait for dialog
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(),'Confirm Lesson Deletion')]")
        )
    )

    # Get all visible buttons
    buttons = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//button")
        )
    )

    visible_buttons = [btn for btn in buttons if btn.is_displayed()]

    # Second last visible button = CANCEL
    cancel_btn = visible_buttons[-2]

    # Scroll to cancel button
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        cancel_btn
    )

    # Click cancel button
    ActionChains(driver).move_to_element(cancel_btn).click().perform()

    time.sleep(1)


# =========================================================
# TP-24-001
# Create lesson with title and description
# =========================================================
def test_create_lesson_with_description(driver):

    lecturer_login(driver)

    title = "Malay Basics"
    description = "Introduction lesson"

    create_lesson(driver, title, description)

    # Verify lesson exists
    assert lesson_exists(driver, title)

    # Verify description displayed
    description_text = driver.find_element(
        By.XPATH,
        f"//*[contains(text(),'{description}')]"
    )

    assert description_text.is_displayed()


# =========================================================
# TP-24-002
# Create lesson with title only
# =========================================================
def test_create_lesson_title_only(driver):

    lecturer_login(driver)

    title = "Malay Basics"

    create_lesson(driver, title)

    # Verify lesson exists
    assert lesson_exists(driver, title)


# =========================================================
# TP-24-003
# Reject empty title
# =========================================================
def test_create_lesson_empty_title(driver):

    lecturer_login(driver)

    click_add_lesson(driver)

    # Fill description only
    fill_lesson_form(
        driver,
        description="Introduction lesson"
    )

    submit_lesson_form(driver)

    time.sleep(1)

    current_url = driver.current_url

    # Verify still at dashboard
    assert "/dashboard" in current_url


# =========================================================
# TP-24-004
# Delete lesson
# =========================================================
def test_delete_lesson(driver):

    lecturer_login(driver)

    title = "Delete Test Lesson"

    create_lesson(driver, title)

    # Verify lesson created
    assert lesson_exists(driver, title)

    # Click trash button
    click_lesson_trash(driver, title)

    # Click delete button
    click_delete_in_dialog(driver)

    # Wait until lesson removed
    WebDriverWait(driver, 10).until(
        lambda d: not lesson_exists(d, title)
    )

    # Verify lesson deleted
    assert not lesson_exists(driver, title)


# =========================================================
# TP-24-005
# Cancel delete lesson
# =========================================================
def test_cancel_delete_lesson(driver):

    lecturer_login(driver)

    title = "Cancel Delete Lesson"

    create_lesson(driver, title)

    # Verify lesson created
    assert lesson_exists(driver, title)

    # Open delete dialog
    click_lesson_trash(driver, title)

    # Click cancel button
    click_cancel_in_dialog(driver)

    # Verify lesson still exists
    assert lesson_exists(driver, title)


# =========================================================
# TP-24-006
# Toggle lesson visibility
# =========================================================
def test_toggle_lesson_visibility(driver):

    lecturer_login(driver)

    title = "Visibility Test Lesson"

    create_lesson(driver, title)

    # Get lesson card
    lesson_card = get_lesson_card(driver, title)

    # Locate visibility button
    visibility_btn = lesson_card.find_element(
        By.XPATH,
        ".//button[contains(@title,'Available') or contains(@title,'Unavailable')]"
    )

    # Click visibility button
    driver.execute_script(
        "arguments[0].click();",
        visibility_btn
    )

    time.sleep(1)

    # Verify lesson still exists
    assert lesson_exists(driver, title)