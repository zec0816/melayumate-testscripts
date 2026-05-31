import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://localhost:5173/"
USERNAME = "22056600"
PASSWORD = "Tzecv22@%"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()


def wait(driver, timeout=20):
    return WebDriverWait(driver, timeout)


def login(driver):
    driver.get(BASE_URL)

    wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Username']")
        )
    ).send_keys(USERNAME)

    wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Password']")
        )
    ).send_keys(PASSWORD)

    login_button = wait(driver).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[normalize-space()='Login' and not(contains(@class,'rounded-l-xl'))]"
            )
        )
    )
    driver.execute_script("arguments[0].click();", login_button)

    wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), \"Today's Stats\")]")
        )
    )


def get_daily_goal_card(driver):
    return wait(driver).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//h3[normalize-space()='Daily Goal']/ancestor::div[contains(@class,'cursor-pointer')]"
            )
        )
    )


def open_daily_goal_dialog(driver):
    card = get_daily_goal_card(driver)

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        card
    )
    driver.execute_script("arguments[0].click();", card)

    return wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='number']")
        )
    )


def get_save_button(driver):
    return wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[normalize-space()='Save']")
        )
    )


def click_save(driver):
    save_button = get_save_button(driver)
    driver.execute_script("arguments[0].click();", save_button)


def click_cancel(driver):
    cancel_button = wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Cancel']")
        )
    )
    driver.execute_script("arguments[0].click();", cancel_button)


def assert_snackbar_message(driver, message):
    assert wait(driver).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//*[contains(@class,'MuiAlert-message') and contains(normalize-space(), '{message}')]"
            )
        )
    )


# =========================================================
# TP-06-001
# Verify student can view daily goal and completion percentage
# =========================================================
def test_tp_06_001_view_daily_goal(driver):

    login(driver)

    # Daily goal card displayed
    card = get_daily_goal_card(driver)

    # Verify daily goal information displayed
    assert "Daily Goal" in card.text
    assert "Completed" in card.text
    assert "%" in card.text
    assert "Click to set a new goal." in card.text


# =========================================================
# TP-06-002
# Update daily goal successfully
# =========================================================
def test_tp_06_002_update_daily_goal_successfully(driver):

    login(driver)

    # Open daily goal dialog
    goal_input = open_daily_goal_dialog(driver)

    # Enter new goal
    goal_input.clear()
    goal_input.send_keys("6")

    # Save goal
    click_save(driver)

    # Verify success message
    assert_snackbar_message(driver, "New goal created!")

    # Verify goal updated
    card = get_daily_goal_card(driver)
    assert "/ 6" in card.text
    assert "Completed" in card.text


# =========================================================
# TP-06-003
# Cancel daily goal update
# =========================================================
def test_tp_06_003_cancel_daily_goal_update(driver):

    login(driver)

    # Store original goal information
    original_card_text = get_daily_goal_card(driver).text

    # Open dialog
    goal_input = open_daily_goal_dialog(driver)

    # Enter new goal
    goal_input.clear()
    goal_input.send_keys("10")

    # Cancel update
    click_cancel(driver)

    # Verify goal remains unchanged
    assert get_daily_goal_card(driver).text == original_card_text


# =========================================================
# TP-06-004
# Reject negative daily goal value
# =========================================================
def test_tp_06_004_reject_negative_daily_goal_value(driver):

    login(driver)

    # Open dialog
    goal_input = open_daily_goal_dialog(driver)

    # Enter invalid value
    goal_input.clear()
    goal_input.send_keys("-1")

    # Save goal
    click_save(driver)

    # Verify validation message
    assert_snackbar_message(driver, "Daily goal must be at least 0.")


# =========================================================
# TP-06-004
# Reject huge daily goal value
# =========================================================
def test_tp_06_004_reject_huge_daily_goal_value(driver):

    login(driver)

    # Open dialog
    goal_input = open_daily_goal_dialog(driver)

    # Enter invalid value
    goal_input.clear()
    goal_input.send_keys("999999")

    # Save goal
    click_save(driver)

    # Verify validation message
    assert_snackbar_message(driver, "Daily goal must be at most 100.")


# =========================================================
# TP-06-004
# Reject decimal daily goal value
# =========================================================
def test_tp_06_004_reject_decimal_daily_goal_value(driver):

    login(driver)

    # Open dialog
    goal_input = open_daily_goal_dialog(driver)

    # Enter decimal value
    goal_input.clear()
    goal_input.send_keys("5.5")

    # Save goal
    click_save(driver)

    # Expected failure if system currently accepts decimals
    assert_snackbar_message(driver, "Daily goal must be a whole number")


# =========================================================
# TP-06-005
# Reject empty daily goal input
# =========================================================
def test_tp_06_005_reject_empty_daily_goal_input(driver):

    login(driver)

    # Open dialog
    goal_input = open_daily_goal_dialog(driver)

    # Leave input empty
    goal_input.clear()

    # Get save button
    save_button = get_save_button(driver)

    # Verify save button disabled
    assert not save_button.is_enabled(), \
        "Save button should be disabled when daily goal input is empty"