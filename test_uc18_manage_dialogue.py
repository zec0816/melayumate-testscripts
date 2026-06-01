import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# =========================
# Basic test configuration
# =========================

BASE_URL = "http://localhost:5173"
USERNAME = "user"
PASSWORD = "User1234*"


@pytest.fixture
def driver():
    """
    Create a Chrome browser instance for each test case.
    After the test finishes, close the browser automatically.
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def wait(driver, seconds=10):
    """
    Reusable explicit wait function.
    This helps Selenium wait until the page element is ready.
    """
    return WebDriverWait(driver, seconds)


# =========================
# Common reusable functions
# =========================
def login(driver):
    driver.get(BASE_URL + "/login")

    username_input = wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Username']"))
    )
    username_input.clear()
    username_input.send_keys(USERNAME)

    password_input = wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_input.clear()
    password_input.send_keys(PASSWORD)

    login_button = wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(),'Login')]"))
    )

    # Safer click for React/Tailwind buttons
    driver.execute_script("arguments[0].click();", login_button)

    wait(driver).until(EC.url_contains("dashboard"))


def go_to_dialogue_form(driver):
    """
    Navigate to the scenario edit page and open the Add Dialogue form.
    Route is /situation because the ScenarioPage uses /situation, not /scenarios.
    """
    driver.get(BASE_URL + "/situation")

    # Click the first scenario card.
    scenario_card = wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h2/ancestor::div[contains(@class,'cursor-pointer')][1]")
        )
    )
    scenario_card.click()

    # Click the edit icon button.
    # The button has title='Edit Scenario', not visible text "Edit".
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Edit Scenario']"))
    ).click()

    # Click Add Dialogue button.
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Add Dialogue')]"))
    ).click()

    # Wait until the dialogue form is visible.
    wait(driver).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='English']"))
    )


def fill_dialogue_form(
    driver,
    english="Good morning",
    malay="Selamat pagi",
    order="1",
    dialogue_type="QUESTION"
):
    """
    Fill in the Add Dialogue form.
    dialogue_type can be QUESTION or RESPONSE.
    """
    if dialogue_type == "QUESTION":
        wait(driver).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Question')]"))
        ).click()
    else:
        wait(driver).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Response')]"))
        ).click()

    english_input = driver.find_element(By.XPATH, "//input[@placeholder='English']")
    malay_input = driver.find_element(By.XPATH, "//input[@placeholder='Malay']")
    order_input = driver.find_element(By.XPATH, "//input[@placeholder='Order (1-5)']")

    english_input.clear()
    malay_input.clear()
    order_input.clear()

    english_input.send_keys(english)
    malay_input.send_keys(malay)
    order_input.send_keys(order)


def click_submit(driver):
    """
    Click the Submit button in the dialogue creation form.
    """
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
    ).click()


def assert_snackbar_message(driver, message):
    """
    Verify that a snackbar or alert message is displayed.
    """
    wait(driver).until(
        EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(),'{message}')]"))
    )


def assert_text_displayed(driver, text):
    """
    Verify that a specific text is displayed on the page.
    """
    wait(driver).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'{text}')]"))
    )
    assert driver.find_element(By.XPATH, f"//*[contains(text(),'{text}')]").is_displayed()


# =========================
# Test cases for UC-18 Manage Dialogue
# =========================

# TP-18-001
def test_tp_18_001_missing_required_fields(driver):
    """
    Verify that the system shows validation error when required fields are empty.
    """
    login(driver)
    go_to_dialogue_form(driver)

    click_submit(driver)

    assert_snackbar_message(driver, "Please fill in English word.")


# TP-18-002
def test_tp_18_002_create_dialogue_successfully(driver):
    """
    Verify that a student can create a dialogue successfully using valid data.
    """
    login(driver)
    go_to_dialogue_form(driver)

    fill_dialogue_form(
        driver,
        english="Good morning test",
        malay="Selamat pagi test",
        order="1",
        dialogue_type="QUESTION"
    )

    click_submit(driver)

    assert_text_displayed(driver, "Selamat pagi test")


# TP-18-003
def test_tp_18_003_duplicate_dialogue_type_and_order(driver):
    """
    Verify that the system rejects duplicate dialogue type and dialogue order.
    This test first creates one dialogue, then tries to create another dialogue
    with the same type and order.
    """
    login(driver)
    go_to_dialogue_form(driver)

    fill_dialogue_form(
        driver,
        english="First duplicate test",
        malay="Dialog pertama",
        order="2",
        dialogue_type="QUESTION"
    )
    click_submit(driver)

    # Open form again after successful add.
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Add Dialogue')]"))
    ).click()

    fill_dialogue_form(
        driver,
        english="Second duplicate test",
        malay="Dialog kedua",
        order="2",
        dialogue_type="QUESTION"
    )
    click_submit(driver)

    # Your backend conflict message may be different.
    # This checks that some conflict/error snackbar appears.
    wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(),'exist') or contains(text(),'duplicate') or contains(text(),'same') or contains(text(),'conflict')]")
        )
    )


# TP-18-004
@pytest.mark.parametrize("invalid_order", ["0", "-1", "abc"])
def test_tp_18_004_invalid_dialogue_order(driver, invalid_order):
    """
    Verify that invalid dialogue order values are not accepted.
    The input should only accept integer values from 1 to 5.
    """
    login(driver)
    go_to_dialogue_form(driver)

    fill_dialogue_form(
        driver,
        english="Invalid order test",
        malay="Ujian susunan salah",
        order=invalid_order,
        dialogue_type="QUESTION"
    )

    click_submit(driver)

    assert_snackbar_message(driver, "Please fill in order.")


# TP-18-005
def test_tp_18_005_duplicate_dialogue_type_and_order(driver):
    """
    Verify that the system rejects a dialogue when the same dialogue type
    and dialogue order already exist.
    """
    login(driver)
    go_to_dialogue_form(driver)

    fill_dialogue_form(
        driver,
        english="Duplicate test 1",
        malay="Dialog duplicate 1",
        order="3",
        dialogue_type="RESPONSE"
    )
    click_submit(driver)

    # Open the form again
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Add Dialogue')]"))
    ).click()

    fill_dialogue_form(
        driver,
        english="Duplicate test 2",
        malay="Dialog duplicate 2",
        order="3",
        dialogue_type="RESPONSE"
    )
    click_submit(driver)

    # Check duplicate error message
    wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(),'already') or contains(text(),'exist') or contains(text(),'same')]")
        )
    )


# TP-18-006
def test_tp_18_006_delete_dialogue(driver):
    """
    Verify that a student can delete an existing dialogue.
    """
    login(driver)

    driver.get(BASE_URL + "/situation")

    scenario_card = wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h2/ancestor::div[contains(@class,'cursor-pointer')][1]")
        )
    )
    scenario_card.click()

    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Edit Scenario']"))
    ).click()

    # Delete button in the dialogue table only contains a trash icon.
    delete_button = wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//tbody//button[.//*[name()='svg']]"))
    )
    delete_button.click()

    assert_snackbar_message(driver, "Dialogue deleted.")


# TP-18-007
def test_tp_18_007_excessively_long_dialogue_input(driver):
    """
    Verify that excessively long dialogue input is restricted by maxLength.
    The DialogueForm input limit is expected to restrict the field length.
    """
    login(driver)
    go_to_dialogue_form(driver)

    long_text = "A" * 40

    fill_dialogue_form(
        driver,
        english=long_text,
        malay=long_text,
        order="4",
        dialogue_type="QUESTION"
    )

    english_value = driver.find_element(
        By.XPATH, "//input[@placeholder='English']"
    ).get_attribute("value")

    malay_value = driver.find_element(
        By.XPATH, "//input[@placeholder='Malay']"
    ).get_attribute("value")

    assert len(english_value) <= 35
    assert len(malay_value) <= 35
