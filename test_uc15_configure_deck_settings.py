"""
test_f15_configure_deck_settings.py
MelayuMate – UC-15 Configure Deck Settings
Automated Selenium WebDriver Test Suite (Python + Pytest)

Feature under test:
  F15 Configure Deck Settings

Test Coverage:
  TC-15-001 → Verify student can open a deck and view existing deck settings.
  TC-15-002 → Verify system applies In Order with English First.
  TC-15-003 → Verify system applies In Order with Malay First.
  TC-15-004 → Verify system applies Shuffled with English First.
  TC-15-005 → Verify system applies Shuffled with Malay First.

Correct flow:
  English First:
    Practice starts with English word.
    Click Show Answer.
    It shows Malay word.
    Click Yes.
    Continue until Finish Practice.

  Malay First:
    Practice starts with Malay word.
    Click Show Answer.
    It shows English word.
    Click Yes.
    Continue until Finish Practice.

  In Order:
    English order should be cat → dog → elephant.
    Malay order should be kucing → anjing → gajah.

  Shuffled:
    The order is random.
    The test checks that Shuffled setting is selected and all Animal cards can be practised.
    It does not force a different order because random can sometimes accidentally match the original order.

Run command:
  pytest -v .\test_f15_configure_deck_settings.py
"""

import os
import re
import time
import pytest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ══════════════════════════════════════════════════════════════════════════════
# Basic Configuration
# ══════════════════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:5173"
FLASHCARD_URL = f"{BASE_URL}/flashcard"

WAIT_TIME = 8

TEST_USERNAME = "low"
TEST_PASSWORD = "Abcdef123!"

TEST_DECK_NAME = "Animal"

ENGLISH_ORDER = ["cat", "dog", "elephant"]
MALAY_ORDER = ["kucing", "anjing", "gajah"]

ENGLISH_TO_MALAY = {
    "cat": "kucing",
    "dog": "anjing",
    "elephant": "gajah",
}

MALAY_TO_ENGLISH = {
    "kucing": "cat",
    "anjing": "dog",
    "gajah": "elephant",
}

ALL_ANIMAL_WORDS = ENGLISH_ORDER + MALAY_ORDER


# ══════════════════════════════════════════════════════════════════════════════
# General Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def wait(driver, seconds=WAIT_TIME):
    return WebDriverWait(driver, seconds)


def xpath_text(text: str) -> str:
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    return "concat(" + ", \"'\", ".join([f"'{part}'" for part in text.split("'")]) + ")"


def save_screenshot(driver, name: str):
    os.makedirs("selenium_screenshots", exist_ok=True)
    driver.save_screenshot(f"selenium_screenshots/{name}.png")


def click_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.15)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.45)


def click_xpath(driver, xpath: str):
    element = wait(driver).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    click_element(driver, element)
    return element


def type_text(element, text: str):
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def element_exists(driver, xpath: str) -> bool:
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except Exception:
        return False


def page_text(driver) -> str:
    return driver.find_element(By.TAG_NAME, "body").text


def page_text_lower(driver) -> str:
    return page_text(driver).lower()


def find_first_visible(driver, xpaths, short_wait=3):
    for xp in xpaths:
        try:
            element = WebDriverWait(driver, short_wait).until(
                EC.visibility_of_element_located((By.XPATH, xp))
            )
            return element
        except Exception:
            pass

    raise AssertionError(f"Cannot find visible element using selectors: {xpaths}")


def visible_button_by_exact_text(driver, text: str):
    buttons = driver.find_elements(By.XPATH, "//button")

    for button in buttons:
        try:
            if button.is_displayed() and button.text.strip().lower() == text.lower():
                return button
        except Exception:
            pass

    return None


def click_button_by_exact_text(driver, text: str):
    button = wait(driver).until(lambda d: visible_button_by_exact_text(d, text))

    if button is None:
        save_screenshot(driver, f"button-{text}-not-found")
        raise AssertionError(f"Cannot find button: {text}")

    click_element(driver, button)
    return button


def click_button_if_exists(driver, text: str, short_wait=2) -> bool:
    try:
        button = WebDriverWait(driver, short_wait).until(
            lambda d: visible_button_by_exact_text(d, text)
        )
        click_element(driver, button)
        return True
    except Exception:
        return False


def word_exists(page: str, word: str) -> bool:
    """
    Check exact word.
    Example:
      cat should match cat.
      cat should not match another long word.
    """
    return re.search(rf"\b{re.escape(word.lower())}\b", page.lower()) is not None


def any_word_exists(page: str, words) -> bool:
    return any(word_exists(page, word) for word in words)


def extract_visible_word(page: str, word_list):
    """
    Return the first matched animal word from page text.
    """
    page = page.lower()

    for word in word_list:
        if word_exists(page, word):
            return word

    return None


# ══════════════════════════════════════════════════════════════════════════════
# Login Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def is_login_form_displayed(driver) -> bool:
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
    login_if_needed(driver)


# ══════════════════════════════════════════════════════════════════════════════
# Deck Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def deck_exists(driver, title: str) -> bool:
    ensure_flashcard_page(driver)

    try:
        driver.find_element(By.XPATH, f"//*[normalize-space()={xpath_text(title)}]")
        return True
    except NoSuchElementException:
        return False


def open_deck(driver, title: str):
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


def open_test_deck(driver):
    ensure_flashcard_page(driver)

    if not deck_exists(driver, TEST_DECK_NAME):
        save_screenshot(driver, "animal-deck-not-found")
        raise AssertionError(
            "Animal deck is not found. Please make sure the Animal deck exists before running this test."
        )

    open_deck(driver, TEST_DECK_NAME)
    wait_for_deck_detail_page(driver)


def wait_for_deck_detail_page(driver):
    try:
        wait(driver).until(
            lambda d: ("in order" in page_text_lower(d) or "shuffled" in page_text_lower(d))
        )
        wait(driver).until(
            lambda d: ("english first" in page_text_lower(d) or "malay first" in page_text_lower(d))
        )
        wait(driver).until(
            lambda d: "practice flashcards" in page_text_lower(d)
        )
    except TimeoutException:
        save_screenshot(driver, "deck-detail-settings-not-found")
        raise AssertionError(
            "Deck detail page loaded, but setting buttons were not found. "
            "Check screenshot: selenium_screenshots/deck-detail-settings-not-found.png"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Deck Settings Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def get_order_button(driver):
    return wait(driver).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(normalize-space(), 'In Order') or contains(normalize-space(), 'Shuffled')]"
            )
        )
    )


def get_language_button(driver):
    return wait(driver).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(normalize-space(), 'English First') or contains(normalize-space(), 'Malay First')]"
            )
        )
    )


def get_order_state(driver) -> str:
    text = get_order_button(driver).text.strip().lower()

    if "shuffled" in text:
        return "shuffled"

    if "in order" in text:
        return "in_order"

    raise AssertionError(f"Unknown order button state: {text}")


def get_language_state(driver) -> str:
    text = get_language_button(driver).text.strip().lower()

    if "malay first" in text:
        return "malay_first"

    if "english first" in text:
        return "english_first"

    raise AssertionError(f"Unknown language button state: {text}")


def set_order(driver, wanted_state: str):
    current_state = get_order_state(driver)

    if current_state != wanted_state:
        click_element(driver, get_order_button(driver))
        wait(driver).until(lambda d: get_order_state(d) == wanted_state)

    assert get_order_state(driver) == wanted_state


def set_language(driver, wanted_state: str):
    current_state = get_language_state(driver)

    if current_state != wanted_state:
        click_element(driver, get_language_button(driver))
        wait(driver).until(lambda d: get_language_state(d) == wanted_state)

    assert get_language_state(driver) == wanted_state


def assert_deck_settings_section_displayed(driver):
    page = page_text_lower(driver)

    assert "in order" in page or "shuffled" in page, \
        "Order setting button is not displayed."

    assert "english first" in page or "malay first" in page, \
        "Language setting button is not displayed."

    assert "practice flashcards" in page, \
        "Practice Flashcards button is not displayed."


# ══════════════════════════════════════════════════════════════════════════════
# Practice Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def wait_for_practice_word(driver, expected_words):
    """
    Wait until the practice page shows one of the expected words.
    """
    try:
        wait(driver).until(
            lambda d: any_word_exists(page_text_lower(d), expected_words)
        )
    except TimeoutException:
        save_screenshot(driver, "practice-word-not-found")
        raise AssertionError(
            f"Expected practice word not found. Expected one of: {expected_words}"
        )

    page = page_text_lower(driver)
    word = extract_visible_word(page, expected_words)

    if word is None:
        save_screenshot(driver, "practice-word-cannot-extract")
        raise AssertionError(
            f"Cannot extract practice word. Expected one of: {expected_words}"
        )

    return word


def wait_for_button(driver, button_text):
    try:
        wait(driver).until(lambda d: visible_button_by_exact_text(d, button_text))
    except TimeoutException:
        save_screenshot(driver, f"{button_text}-button-not-found")
        raise AssertionError(f"{button_text} button not found.")


def complete_practice_session(driver, first_language: str, expected_order=None):
    """
    Complete the Animal deck practice session.

    first_language:
      english_first
      malay_first

    expected_order:
      For In Order:
        English First → ["cat", "dog", "elephant"]
        Malay First → ["kucing", "anjing", "gajah"]

      For Shuffled:
        None, because shuffled order is random.
    """
    click_button_by_exact_text(driver, "Practice Flashcards")

    if first_language == "english_first":
        front_words = ENGLISH_ORDER
        answer_map = ENGLISH_TO_MALAY
    else:
        front_words = MALAY_ORDER
        answer_map = MALAY_TO_ENGLISH

    seen_front_words = []

    for index in range(3):
        # Check front card word
        if expected_order is not None:
            expected_front_word = expected_order[index]
            front_word = wait_for_practice_word(driver, [expected_front_word])
            assert front_word == expected_front_word, \
                f"Wrong card order. Expected {expected_front_word}, but got {front_word}."
        else:
            front_word = wait_for_practice_word(driver, front_words)

        seen_front_words.append(front_word)

        # Click Show Answer
        wait_for_button(driver, "Show Answer")
        click_button_by_exact_text(driver, "Show Answer")

        # Check answer word
        expected_answer = answer_map[front_word]
        answer_word = wait_for_practice_word(driver, [expected_answer])

        assert answer_word == expected_answer, \
            f"Wrong answer shown. For {front_word}, expected {expected_answer}, but got {answer_word}."

        # Click Yes
        wait_for_button(driver, "Yes")
        click_button_by_exact_text(driver, "Yes")

        # Continue or finish
        if index < 2:
            wait_for_button(driver, "Next")
            click_button_by_exact_text(driver, "Next")
        else:
            wait_for_button(driver, "Finish Practice")
            click_button_by_exact_text(driver, "Finish Practice")

    # For shuffled, make sure all 3 Animal cards were practised.
    if expected_order is None:
        assert set(seen_front_words) == set(front_words), \
            f"Shuffled practice did not show all expected cards. Got: {seen_front_words}"

    return seen_front_words


# ══════════════════════════════════════════════════════════════════════════════
# Pytest Driver
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    d = webdriver.Chrome(options=options)

    d.implicitly_wait(0.5)

    login_if_needed(d)

    yield d

    d.quit()


# ══════════════════════════════════════════════════════════════════════════════
# UC-15 Configure Deck Settings Test Cases
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# TP-15-001 | TC-15-001
# Verify student can open a deck and view existing deck settings.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_15_001_open_deck_and_view_existing_deck_settings(driver):
    open_test_deck(driver)

    assert_deck_settings_section_displayed(driver)

    save_screenshot(driver, "TC-15-001-view-existing-deck-settings")


# ─────────────────────────────────────────────────────────────────────────────
# TP-15-002 | TC-15-002
# Verify system applies In Order with English First.
# Expected practice flow:
#   cat → kucing
#   dog → anjing
#   elephant → gajah
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_15_002_apply_default_order_with_english_first(driver):
    open_test_deck(driver)

    set_order(driver, "in_order")
    set_language(driver, "english_first")

    assert get_order_state(driver) == "in_order"
    assert get_language_state(driver) == "english_first"

    completed_order = complete_practice_session(
        driver,
        first_language="english_first",
        expected_order=ENGLISH_ORDER
    )

    assert completed_order == ENGLISH_ORDER

    save_screenshot(driver, "TC-15-002-in-order-english-first")


# ─────────────────────────────────────────────────────────────────────────────
# TP-15-003 | TC-15-003
# Verify system applies In Order with Malay First.
# Expected practice flow:
#   kucing → cat
#   anjing → dog
#   gajah → elephant
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_15_003_apply_default_order_with_malay_first(driver):
    open_test_deck(driver)

    set_order(driver, "in_order")
    set_language(driver, "malay_first")

    assert get_order_state(driver) == "in_order"
    assert get_language_state(driver) == "malay_first"

    completed_order = complete_practice_session(
        driver,
        first_language="malay_first",
        expected_order=MALAY_ORDER
    )

    assert completed_order == MALAY_ORDER

    save_screenshot(driver, "TC-15-003-in-order-malay-first")


# ─────────────────────────────────────────────────────────────────────────────
# TP-15-004 | TC-15-004
# Verify system applies Shuffled with English First.
# Expected:
#   Front card is English.
#   Answer is Malay.
#   All 3 Animal cards are completed.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_15_004_apply_random_order_with_english_first(driver):
    open_test_deck(driver)

    set_order(driver, "shuffled")
    set_language(driver, "english_first")

    assert get_order_state(driver) == "shuffled"
    assert get_language_state(driver) == "english_first"

    completed_order = complete_practice_session(
        driver,
        first_language="english_first",
        expected_order=None
    )

    assert set(completed_order) == set(ENGLISH_ORDER)

    save_screenshot(driver, "TC-15-004-shuffled-english-first")


# ─────────────────────────────────────────────────────────────────────────────
# TP-15-005 | TC-15-005
# Verify system applies Shuffled with Malay First.
# Expected:
#   Front card is Malay.
#   Answer is English.
#   All 3 Animal cards are completed.
# ─────────────────────────────────────────────────────────────────────────────
def test_TC_15_005_apply_random_order_with_malay_first_and_save_settings(driver):
    open_test_deck(driver)

    set_order(driver, "shuffled")
    set_language(driver, "malay_first")

    assert get_order_state(driver) == "shuffled"
    assert get_language_state(driver) == "malay_first"

    completed_order = complete_practice_session(
        driver,
        first_language="malay_first",
        expected_order=None
    )

    assert set(completed_order) == set(MALAY_ORDER)

    save_screenshot(driver, "TC-15-005-shuffled-malay-first")