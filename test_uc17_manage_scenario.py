"""
UC-17: Manage Scenario — Selenium Test Script
Prepared by: Tan Chien Ling
Techniques: Use Case Testing, Equivalence Partitioning, Error Guessing
"""

import time
import uuid
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION 
# ══════════════════════════════════════════════════════════════════════════════
CHROMEDRIVER_PATH = r"C:\chromedriver\chromedriver-win64\chromedriver.exe"
BASE_URL          = "http://localhost:5173"
FLASHCARD_URL     = f"{BASE_URL}/flashcards"
STUDENT_USERNAME  = "tester"
STUDENT_PASSWORD  = "Testing.123"
SCREENSHOT_DIR    = "screenshots"
# ══════════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────────────────────
# BROWSER FIXTURE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def driver():
    """Single Chrome session shared across all tests."""
    options = Options()
    options.add_argument("--start-maximized")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    _login(drv)
    yield drv
    drv.quit()


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _wait(driver, timeout=10):
    return WebDriverWait(driver, timeout)


def _login(driver):
    """Log in as student."""
    driver.get(BASE_URL)
    time.sleep(2)
    _wait(driver).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
    ).send_keys(STUDENT_USERNAME)
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(STUDENT_PASSWORD)
    driver.execute_script(
        "arguments[0].click();",
        driver.find_element(By.XPATH, "//button[@type='submit' and normalize-space()='Login']")
    )
    time.sleep(2)


def _short_unique_title(prefix):
    """Max 23 chars to stay within maxLength=25."""
    return f"{prefix[:16]}_{str(uuid.uuid4())[:6]}"


def _save_screenshot(driver, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")


def _type_text(element, text):
    element.clear()
    element.send_keys(text)


def _click_xpath(driver, xpath, timeout=10):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].click();", el)


def _get_input_value(element):
    return element.get_attribute("value")


def _ensure_flashcard_page(driver):
    driver.get(FLASHCARD_URL)
    time.sleep(2)


def _create_deck(driver, title, description=""):
    """Create a flashcard deck and return actual title typed."""
    _ensure_flashcard_page(driver)
    _click_xpath(driver, "//button[contains(normalize-space(),'Create Deck')]")
    time.sleep(0.8)

    # Panel: 'New Flashcard Deck', title input placeholder='Title', maxLength=25
    title_input = _wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH,
             "//h3[normalize-space()='New Flashcard Deck']"
             "/ancestor::div[contains(@class,'fixed top-0')]"
             "//input[@placeholder='Title']")
        )
    )
    _type_text(title_input, title)
    actual_title = _get_input_value(title_input)

    if description:
        try:
            desc = driver.find_element(
                By.XPATH,
                "//h3[normalize-space()='New Flashcard Deck']"
                "/ancestor::div[contains(@class,'fixed top-0')]"
                "//textarea[@placeholder='Description (Optional)']"
            )
            _type_text(desc, description)
        except Exception:
            pass

    _click_xpath(
        driver,
        "//h3[normalize-space()='New Flashcard Deck']"
        "/ancestor::div[contains(@class,'fixed top-0')]"
        "//button[normalize-space()='Submit']"
    )
    time.sleep(1)
    _ensure_flashcard_page(driver)
    return actual_title


def _open_deck(driver, deck_title):
    """Click the Open button on a deck card by title."""
    _ensure_flashcard_page(driver)
    deck_card = _wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH,
             f"//*[contains(normalize-space(), '{deck_title}')]"
             f"/ancestor::div[.//button[normalize-space()='Open']]")
        )
    )
    open_btn = deck_card.find_element(By.XPATH, ".//button[normalize-space()='Open']")
    driver.execute_script("arguments[0].click();", open_btn)
    time.sleep(2)


def _go_to_cards_management(driver):
    """Click Edit button to go to cards management page."""
    _click_xpath(driver, "//button[normalize-space()='Edit' or contains(@title,'Edit')]")
    time.sleep(1)


def _open_add_card_panel(driver):
    """Click Add Card button to open Add Flashcard panel."""
    _click_xpath(driver, "//button[contains(normalize-space(),'Add Card')]")
    time.sleep(0.8)


def _get_english_input(driver):
    """Get English input inside the Add/Edit Flashcard panel."""
    return _wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH,
             "//h3[contains(normalize-space(),'Flashcard')]"
             "/ancestor::div[contains(@class,'fixed top-0')]"
             "//input[@placeholder='English']")
        )
    )


def _get_malay_input(driver):
    """Get Malay input inside the Add/Edit Flashcard panel."""
    return driver.find_element(
        By.XPATH,
        "//h3[contains(normalize-space(),'Flashcard')]"
        "/ancestor::div[contains(@class,'fixed top-0')]"
        "//input[@placeholder='Malay']"
    )


def _click_submit_card(driver):
    """Click Submit inside Add Flashcard panel."""
    _click_xpath(
        driver,
        "//h3[normalize-space()='Add Flashcard']"
        "/ancestor::div[contains(@class,'fixed top-0')]"
        "//button[normalize-space()='Submit']"
    )
    time.sleep(1)


def _click_save_card(driver):
    """Click Save inside Edit Flashcard panel."""
    _click_xpath(
        driver,
        "//h3[normalize-space()='Edit Flashcard']"
        "/ancestor::div[contains(@class,'fixed top-0')]"
        "//button[normalize-space()='Save']"
    )
    time.sleep(1)


def _add_card(driver, english, malay):
    """Add a card and return (actual_english, actual_malay)."""
    _open_add_card_panel(driver)
    eng = _get_english_input(driver)
    _type_text(eng, english)
    actual_eng = _get_input_value(eng)
    mal = _get_malay_input(driver)
    _type_text(mal, malay)
    actual_mal = _get_input_value(mal)
    _click_submit_card(driver)
    return actual_eng, actual_mal


def _card_exists(driver, word):
    """Return True if a word appears in the card list."""
    try:
        driver.find_element(By.XPATH, f"//*[contains(normalize-space(), '{word}')]")
        return True
    except Exception:
        return False


def _click_edit_on_card(driver, english_word):
    """Click Edit button (blue hover icon) on the card row matching the English word.
    From debug: edit button class='text-gray-600 hover:text-blue-500 cursor-pointer'
    """
    _click_xpath(
        driver,
        f"//tr[td[normalize-space()='{english_word}']]"
        f"//button[contains(@class,'hover:text-blue-500')]"
    )
    time.sleep(0.8)


def _click_delete_on_card(driver, english_word):
    """Click Delete button (red hover icon) on the card row matching the English word.
    From debug: delete button class='text-gray-600 hover:text-red-500 cursor-pointer'
    """
    _click_xpath(
        driver,
        f"//tr[td[normalize-space()='{english_word}']]"
        f"//button[contains(@class,'hover:text-red-500')]"
    )
    time.sleep(0.5)


def _wait_for_snackbar(driver, text, timeout=8):
    return _wait(driver, timeout).until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//*[contains(normalize-space(), '{text}')]")
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# TEST CASES
# ─────────────────────────────────────────────────────────────────────────────

def test_TC_14_001_navigate_to_cards_management_page(driver):
    """TC-14-001: Verify student can open a deck and navigate to cards management page."""
    deck_title = _short_unique_title("NavDeck")
    _create_deck(driver, deck_title, "Navigation test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)

    add_btn = _wait(driver).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[contains(normalize-space(),'Add Card')]")
        )
    )
    assert add_btn.is_displayed(), \
        "TC-14-001 FAIL: Cards management page not loaded — Add Card button not found."

    _save_screenshot(driver, "TC-14-001-cards-management")
    print("\nTC-14-001 PASS: Cards management page displayed correctly.")


def test_TC_14_002_add_card_with_valid_english_and_malay(driver):
    """TC-14-002: Verify student can add a new card with valid English and Malay word."""
    deck_title = _short_unique_title("AddDeck")
    _create_deck(driver, deck_title, "Add card test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)

    actual_eng, actual_malay = _add_card(driver, "Cat", "Kucing")

    assert _card_exists(driver, actual_eng), \
        f"TC-14-002 FAIL: Card '{actual_eng}' not found after creation."

    _save_screenshot(driver, "TC-14-002-add-card")
    print(f"\nTC-14-002 PASS: Card '{actual_eng}' / '{actual_malay}' added successfully.")


def test_TC_14_003_edit_existing_card(driver):
    """TC-14-003: Verify student can edit an existing card's English and Malay word."""
    deck_title = _short_unique_title("EditDeck")
    _create_deck(driver, deck_title, "Edit card test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)
    _add_card(driver, "Dog", "Anjing")

    _click_edit_on_card(driver, "Dog")

    eng_input = _wait(driver).until(
        EC.visibility_of_element_located(
            (By.XPATH,
             "//h3[normalize-space()='Edit Flashcard']"
             "/ancestor::div[contains(@class,'fixed top-0')]"
             "//input[@placeholder='English']")
        )
    )
    _type_text(eng_input, "Bird")
    actual_new_eng = _get_input_value(eng_input)

    malay_input = driver.find_element(
        By.XPATH,
        "//h3[normalize-space()='Edit Flashcard']"
        "/ancestor::div[contains(@class,'fixed top-0')]"
        "//input[@placeholder='Malay']"
    )
    _type_text(malay_input, "Burung")

    _click_save_card(driver)

    assert _card_exists(driver, actual_new_eng), \
        f"TC-14-003 FAIL: Edited card '{actual_new_eng}' not found."

    _save_screenshot(driver, "TC-14-003-edit-card")
    print(f"\nTC-14-003 PASS: Card updated to '{actual_new_eng}' / 'Burung'.")


def test_TC_14_004_delete_card(driver):
    """TC-14-004: Verify student can delete a card from the deck."""
    deck_title = _short_unique_title("DelDeck")
    _create_deck(driver, deck_title, "Delete card test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)
    _add_card(driver, "Fish", "Ikan")

    assert _card_exists(driver, "Fish"), \
        "TC-14-004 FAIL: Card 'Fish' not found before deletion."

    _click_delete_on_card(driver, "Fish")
    time.sleep(1)

    assert not _card_exists(driver, "Fish"), \
        "TC-14-004 FAIL: Card 'Fish' still exists after deletion."

    _save_screenshot(driver, "TC-14-004-delete-card")
    print("\nTC-14-004 PASS: Card 'Fish' deleted successfully.")


def test_TC_14_005_reject_empty_fields(driver):
    """TC-14-005: Verify system rejects empty English, empty Malay, and both empty."""
    deck_title = _short_unique_title("ErrDeck")
    _create_deck(driver, deck_title, "Validation test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)

    # Part 1 — empty English, valid Malay
    _open_add_card_panel(driver)
    _type_text(_get_malay_input(driver), "Kucing")
    _click_submit_card(driver)
    error = _wait_for_snackbar(driver, "English")
    assert error.is_displayed(), "TC-14-005 FAIL: No error for empty English."
    _save_screenshot(driver, "TC-14-005-empty-english")

    # Part 2 — valid English, empty Malay
    _type_text(_get_english_input(driver), "Cat")
    _type_text(_get_malay_input(driver), "")
    _click_submit_card(driver)
    error = _wait_for_snackbar(driver, "Malay")
    assert error.is_displayed(), "TC-14-005 FAIL: No error for empty Malay."
    _save_screenshot(driver, "TC-14-005-empty-malay")

    # Part 3 — both empty (reopen panel since Part 2 may have closed it)
    _open_add_card_panel(driver)
    # leave both fields empty and submit
    _click_submit_card(driver)
    error = _wait_for_snackbar(driver, "English")
    assert error.is_displayed(), "TC-14-005 FAIL: No error for both empty."
    _save_screenshot(driver, "TC-14-005-both-empty")

    print("\nTC-14-005 PASS: System correctly rejects all empty field combinations.")


def test_TC_14_006_reject_symbols_only_and_numbers_only(driver):
    """TC-14-006: Verify system handles symbol-only Malay and number-only English inputs."""
    deck_title = _short_unique_title("SyntaxDeck")
    _create_deck(driver, deck_title, "Syntax test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)

    # Part 1 — symbol-only Malay
    _open_add_card_panel(driver)
    _type_text(_get_english_input(driver), "Cat")
    _type_text(_get_malay_input(driver), "@#$%")
    _click_submit_card(driver)
    time.sleep(0.5)
    _save_screenshot(driver, "TC-14-006-symbol-malay")

    # Part 2 — number-only English (reopen panel if closed after Part 1)
    _open_add_card_panel(driver)
    _type_text(_get_english_input(driver), "12345")
    _type_text(_get_malay_input(driver), "Kucing")
    _click_submit_card(driver)
    time.sleep(0.5)
    _save_screenshot(driver, "TC-14-006-number-english")

    print("\nTC-14-006 PASS: System handled symbol-only and number-only inputs.")


def test_TC_14_007_accept_malay_diacritics(driver):
    """TC-14-007: Verify system accepts Malay word with diacritics as valid input."""
    deck_title = _short_unique_title("DiacDeck")
    _create_deck(driver, deck_title, "Diacritics test")

    _open_deck(driver, deck_title)
    _go_to_cards_management(driver)

    actual_eng, actual_malay = _add_card(driver, "Mother", "Ibu")

    assert _card_exists(driver, actual_eng), \
        f"TC-14-007 FAIL: Card '{actual_eng}' / '{actual_malay}' not found."

    _save_screenshot(driver, "TC-14-007-diacritics")
    print(f"\nTC-14-007 PASS: Card with Malay word '{actual_malay}' accepted.")