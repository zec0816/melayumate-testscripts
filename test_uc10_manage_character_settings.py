"""
test_uc10_manage_character_settings.py
MelayuMate – UC-10 Manage Character Settings
Automated test suite using Selenium WebDriver (Python)

Test Coverage:
  TC-10-001 | TCOV-10-001, TCOV-10-002, TCOV-10-008
  TC-10-002 | TCOV-10-003, TCOV-10-009
  TC-10-003 | TCOV-10-004
  TC-10-004 | TCOV-10-005, TCOV-10-007, TCOV-10-010
  TC-10-005 | TCOV-10-006

Pre-conditions:
  - MelayuMate student frontend running at BASE_URL (default: http://localhost:5173)
  - TWO_CHAR_USER owns PRIMARY_CHAR (primary) and SECONDARY_CHAR (secondary)
  - ONE_CHAR_USER owns only PRIMARY_CHAR (primary), no secondary character
  - Both accounts must be registered and verified in the system
  - TC-10-003 additionally requires TWO_CHAR_USER to have:
      * At least one flashcard list with at least one card
      * At least one scenario with a 'ques'-type dialogue as its first message
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# ──────────────────────────────────────────────────────────────────────────────
# Configuration — update character names to match your database
# ──────────────────────────────────────────────────────────────────────────────
BASE_URL         = "http://localhost:5173"
LOGIN_URL        = f"{BASE_URL}/login"

TWO_CHAR_USER    = "user1"
TWO_CHAR_PASS    = "123456@As"

ONE_CHAR_USER    = "user2"
ONE_CHAR_PASS    = "123456@As"

PRIMARY_CHAR     = "PyroBot"    # primary character owned by both users
SECONDARY_CHAR   = "PoisonBot"  # secondary character owned only by TWO_CHAR_USER

WAIT_TIMEOUT     = 20  # seconds


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(WAIT_TIMEOUT)
    yield drv
    drv.quit()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def login(driver, username, password):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    driver.find_element(By.XPATH, "//input[@placeholder='Username']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    wait.until(EC.url_contains("dashboard"))


def navigate_to_character_page(driver):
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[normalize-space()='Character']")
    )).click()
    wait.until(EC.url_contains("character"))
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h2[contains(text(),'Your Team')] | //h1[contains(text(),'Choose Your First')]")
    ))


def card_xpath(char_name):
    return f"//div[contains(@class,'rounded-2xl') and .//h3[contains(text(),'{char_name}')]]"


def go_to_character_page_by_url(driver):
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    driver.get(f"{BASE_URL}/character")
    wait.until(EC.url_contains("character"))
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//h2[contains(text(),'Your Team')] | //h1[contains(text(),'Choose Your First')]")
    ))


def reset_primary(driver, original_primary):
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        go_to_character_page_by_url(driver)
        btn = driver.find_element(
            By.XPATH, f"{card_xpath(original_primary)}//button[normalize-space()='Set as Primary']"
        )
        btn.click()
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f"{card_xpath(original_primary)}//*[contains(text(),'Primary')]")
        ))
    except NoSuchElementException:
        pass  # already primary, no reset needed


def ensure_primary_char(driver):
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    driver.implicitly_wait(0)
    needs_reset = driver.find_elements(
        By.XPATH, f"{card_xpath(PRIMARY_CHAR)}//button[normalize-space()='Set as Primary']"
    )
    driver.implicitly_wait(WAIT_TIMEOUT)
    if needs_reset:
        needs_reset[0].click()
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f"{card_xpath(PRIMARY_CHAR)}//*[contains(text(),'Primary')]")
        ))


# ══════════════════════════════════════════════════════════════════════════════
# TC-10-001 | TCOV-10-001, TCOV-10-002, TCOV-10-008
# ══════════════════════════════════════════════════════════════════════════════
def test_TC_10_001_navigate_to_character_page_and_view_characters(driver):
    login(driver, TWO_CHAR_USER, TWO_CHAR_PASS)
    navigate_to_character_page(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    ensure_primary_char(driver)

    # TCOV-10-001: URL contains 'character'
    assert "character" in driver.current_url.lower(), \
        "Expected URL to contain 'character' after navigation."

    # TCOV-10-002: Both characters are visible
    primary_el = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//h3[contains(text(),'{PRIMARY_CHAR}')]")
    ))
    assert primary_el.is_displayed(), f"{PRIMARY_CHAR} should be visible on the character page."

    secondary_el = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//h3[contains(text(),'{SECONDARY_CHAR}')]")
    ))
    assert secondary_el.is_displayed(), f"{SECONDARY_CHAR} should be visible on the character page."

    # TCOV-10-008: Correct badges shown
    primary_badge = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"{card_xpath(PRIMARY_CHAR)}//*[contains(text(),'Primary')]")
    ))
    assert primary_badge.is_displayed(), f"{PRIMARY_CHAR} should display the '★ Primary' badge."

    owned_badge = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//*[contains(text(),'Owned')]")
    ))
    assert owned_badge.is_displayed(), f"{SECONDARY_CHAR} should display the 'Owned' badge."


# ══════════════════════════════════════════════════════════════════════════════
# TC-10-002 | TCOV-10-003, TCOV-10-009
# ══════════════════════════════════════════════════════════════════════════════
def test_TC_10_002_set_as_primary_button_visible_and_processes_switch(driver):
    login(driver, TWO_CHAR_USER, TWO_CHAR_PASS)
    navigate_to_character_page(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    ensure_primary_char(driver)

    # TCOV-10-009: Button is visible and enabled on secondary character card
    set_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//button[normalize-space()='Set as Primary']")
    ))
    assert set_btn.is_displayed(), "'Set as Primary' button should be visible on secondary character card."
    assert set_btn.is_enabled(), "'Set as Primary' button should be enabled on secondary character card."

    # TCOV-10-003: System processes the switch
    set_btn.click()
    new_primary_badge = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//*[contains(text(),'Primary')]")
    ))
    assert new_primary_badge.is_displayed(), \
        f"{SECONDARY_CHAR} should display '★ Primary' badge after clicking 'Set as Primary'."

    reset_primary(driver, PRIMARY_CHAR)


# ══════════════════════════════════════════════════════════════════════════════
# TC-10-003 | TCOV-10-004
# ══════════════════════════════════════════════════════════════════════════════
def test_TC_10_003_characters_swap_and_new_primary_shown_across_features(driver):
    login(driver, TWO_CHAR_USER, TWO_CHAR_PASS)
    navigate_to_character_page(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    ensure_primary_char(driver)

    try:
        # Swap secondary to primary
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//button[normalize-space()='Set as Primary']")
        )).click()

        # Character page: badges swapped correctly
        new_primary_badge = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//*[contains(text(),'Primary')]")
        ))
        assert new_primary_badge.is_displayed(), f"{SECONDARY_CHAR} should show '★ Primary' badge after swap."

        old_primary_owned = wait.until(EC.presence_of_element_located(
            (By.XPATH, f"{card_xpath(PRIMARY_CHAR)}//*[contains(text(),'Owned')]")
        ))
        assert old_primary_owned.is_displayed(), f"{PRIMARY_CHAR} should show 'Owned' badge after swap."

        # Chat room: new primary avatar shown
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Dashboard']")
        )).click()
        wait.until(EC.url_contains("dashboard"))

        chat_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class,'bg-blue-600') and contains(@class,'rounded-full')]")
        ))
        chat_btn.click()

        msg_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='Write a message...']")
        ))
        msg_input.send_keys("test")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1)

        chat_avatar = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//img[contains(@class,'w-14') and contains(@class,'rounded-full')]")
        ))
        assert chat_avatar.is_displayed(), "Character avatar should appear in chat room after primary swap."

        # Flashcard practice: new primary avatar shown
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Flashcard']")
        )).click()
        wait.until(EC.url_contains("flashcard"))

        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Open']")
        )).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(normalize-space(),'Practice')]")
        )).click()

        fc_avatar = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//img[@alt='Character Avatar']")
        ))
        assert fc_avatar.is_displayed(), "Character avatar should appear in flashcard practice after primary swap."

        # Dialogue practice: new primary avatar shown
        driver.get(f"{BASE_URL}/situation")
        wait.until(EC.url_contains("situation"))

        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'rounded-2xl') and contains(@class,'cursor-pointer')][1]")
        )).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(normalize-space(),'Start')]")
        )).click()

        dlg_avatar = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//img[@alt='Character Avatar']")
        ))
        assert dlg_avatar.is_displayed(), "Character avatar should appear in dialogue practice after primary swap."

    finally:
        reset_primary(driver, PRIMARY_CHAR)


# ══════════════════════════════════════════════════════════════════════════════
# TC-10-004 | TCOV-10-005, TCOV-10-007, TCOV-10-010
# ══════════════════════════════════════════════════════════════════════════════
def test_TC_10_004_no_switch_option_when_student_owns_one_character(driver):
    login(driver, ONE_CHAR_USER, ONE_CHAR_PASS)
    navigate_to_character_page(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # TCOV-10-005, TCOV-10-010: No Set as Primary button
    driver.implicitly_wait(0)
    set_primary_buttons = driver.find_elements(By.XPATH, "//button[normalize-space()='Set as Primary']")
    secondary_elements = driver.find_elements(
        By.XPATH,
        f"//h2[contains(text(),'Your Team')]/following-sibling::div//h3[contains(text(),'{SECONDARY_CHAR}')]"
    )
    driver.implicitly_wait(WAIT_TIMEOUT)

    assert len(set_primary_buttons) == 0, \
        "'Set as Primary' button should NOT be present when student owns only 1 character."

    # TCOV-10-007: Primary character shown with Primary badge
    primary_badge = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"{card_xpath(PRIMARY_CHAR)}//*[contains(text(),'Primary')]")
    ))
    assert primary_badge.is_displayed(), f"{PRIMARY_CHAR} should be displayed as the only primary character."

    # TCOV-10-007: Secondary character NOT present in owned team
    assert len(secondary_elements) == 0, \
        f"{SECONDARY_CHAR} should NOT be displayed when student owns only 1 character."


# ══════════════════════════════════════════════════════════════════════════════
# TC-10-005 | TCOV-10-006
# ══════════════════════════════════════════════════════════════════════════════
def test_TC_10_005_switch_allowed_when_student_owns_two_characters(driver):
    login(driver, TWO_CHAR_USER, TWO_CHAR_PASS)
    navigate_to_character_page(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    ensure_primary_char(driver)

    # TCOV-10-006: Button enabled and swap succeeds
    set_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//button[normalize-space()='Set as Primary']")
    ))
    assert set_btn.is_displayed(), "'Set as Primary' button should be visible with 2 characters."
    assert set_btn.is_enabled(), "'Set as Primary' button should be enabled with 2 characters."

    set_btn.click()
    new_primary = wait.until(EC.presence_of_element_located(
        (By.XPATH, f"{card_xpath(SECONDARY_CHAR)}//*[contains(text(),'Primary')]")
    ))
    assert new_primary.is_displayed(), \
        f"Characters should swap; {SECONDARY_CHAR} should be '★ Primary'."

    reset_primary(driver, PRIMARY_CHAR)
