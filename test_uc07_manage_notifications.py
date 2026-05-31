"""
test_uc07_manage_notifications.py
MelayuMate – UC-07 Manage Notifications
Automated test suite using Selenium WebDriver (Python)

Test Coverage:
  TC-07-001 | TCOV-07-001, TCOV-07-002, TCOV-07-009
  TC-07-002 | TCOV-07-003, TCOV-07-010
  TC-07-003 | TCOV-07-004, TCOV-07-011, TCOV-07-012
  TC-07-004 | TCOV-07-005, TCOV-07-013
  TC-07-005 | TCOV-07-006, TCOV-07-007, TCOV-07-008

Pre-conditions:
  - MelayuMate student frontend running at BASE_URL (default: http://localhost:5173)
  - NOTIF_USER owns an account with at least 1 unread notification
  - NO_NOTIF_USER owns an account with 0 notifications
  - Both accounts must be registered and verified in the system

SQL to seed a notification for NOTIF_USER:
  INSERT INTO notifications (notification_id, user_id, message, is_read, created_at)
  VALUES ('notif_test_001',
          (SELECT user_id FROM users WHERE username = 'user1'),
          'New Lesson Available: Kata Nama', 0, NOW());
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
BASE_URL      = "http://localhost:5173"
LOGIN_URL     = f"{BASE_URL}/login"

NOTIF_USER    = "user1"
NOTIF_PASS    = "123456@As"

NO_NOTIF_USER = "user2"
NO_NOTIF_PASS = "123456@As"

WAIT_TIMEOUT  = 20  # seconds

# XPath for the notification bell button (NotificationBell.jsx)
BELL_XPATH = (
    "//button[contains(@class,'p-2') and contains(@class,'text-gray-400') "
    "and contains(@class,'cursor-pointer')]"
)

MARK_READ_XPATH = (
    "//button[contains(normalize-space(),'Mark') and contains(normalize-space(),'read')]"
    " | //button[contains(normalize-space(),'mark') and contains(normalize-space(),'read')]"
)


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
def logout(driver):
    """Clear browser session so a fresh login can proceed."""
    driver.delete_all_cookies()
    if driver.current_url.startswith("http"):
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")


def login(driver, username, password):
    logout(driver)
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    driver.find_element(By.XPATH, "//input[@placeholder='Username']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    wait.until(EC.url_contains("dashboard"))


def click_bell(driver):
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    bell = wait.until(EC.element_to_be_clickable((By.XPATH, BELL_XPATH)))
    bell.click()
    time.sleep(0.5)


# ══════════════════════════════════════════════════════════════════════════════
# TP-07-001 | TC-07-001
# Covers: TCOV-07-001, TCOV-07-002, TCOV-07-009
# Objective: Verify student can navigate to dashboard page and system retrieves
#            unread notifications successfully.
# ══════════════════════════════════════════════════════════════════════════════
def test_tp_07_001_navigate_to_dashboard_and_retrieve_notifications(driver):
    login(driver, NOTIF_USER, NOTIF_PASS)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # TCOV-07-001: URL contains dashboard
    assert "dashboard" in driver.current_url.lower(), \
        "Expected URL to contain 'dashboard' after login."

    # TCOV-07-002, TCOV-07-009: Bell icon visible — notifications retrieved
    bell = wait.until(EC.presence_of_element_located((By.XPATH, BELL_XPATH)))
    assert bell.is_displayed(), \
        "Bell icon should be visible on dashboard after notifications are retrieved."


# ══════════════════════════════════════════════════════════════════════════════
# TP-07-002 | TC-07-002
# Covers: TCOV-07-003, TCOV-07-010
# Objective: Verify student can click bell icon and view notification list
#            in collapsible format.
# ══════════════════════════════════════════════════════════════════════════════
def test_tp_07_002_click_bell_icon_opens_notification_list(driver):
    login(driver, NOTIF_USER, NOTIF_PASS)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    click_bell(driver)

    notif_panel = wait.until(EC.presence_of_element_located(
        (By.XPATH,
         "//div[contains(.,'Mark') and contains(.,'read')]"
         " | //*[contains(@class,'notification') and ("
         "contains(@class,'panel') or contains(@class,'dropdown') "
         "or contains(@class,'list') or contains(@class,'drawer'))]")
    ))
    assert notif_panel.is_displayed(), \
        "Notification list should be displayed in collapsible format after clicking bell icon."


# ══════════════════════════════════════════════════════════════════════════════
# TP-07-003 | TC-07-003
# Covers: TCOV-07-004, TCOV-07-011, TCOV-07-012
# Objective: Verify student can mark all notifications as read and notifications
#            are not visible on page reload.
# ══════════════════════════════════════════════════════════════════════════════
def test_tp_07_003_mark_all_as_read_clears_notifications(driver):
    login(driver, NOTIF_USER, NOTIF_PASS)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    click_bell(driver)

    mark_btn = wait.until(EC.element_to_be_clickable((By.XPATH, MARK_READ_XPATH)))
    assert mark_btn.is_displayed(), \
        "'Mark all as read' button should be visible when notifications exist."
    mark_btn.click()
    time.sleep(1)

    driver.refresh()
    wait.until(EC.url_contains("dashboard"))
    time.sleep(1)

    click_bell(driver)
    time.sleep(1)

    driver.implicitly_wait(0)
    unread_badges = driver.find_elements(
        By.XPATH,
        "//*[contains(@class,'badge') and contains(@class,'unread')]"
        " | //*[contains(@class,'notification-count') and string-length(normalize-space(.))>0]"
        " | //*[@aria-label='unread notifications']"
    )
    driver.implicitly_wait(WAIT_TIMEOUT)
    assert len(unread_badges) == 0, \
        "No unread badge should be visible after marking all as read and reloading."


# ══════════════════════════════════════════════════════════════════════════════
# TP-07-004 | TC-07-004
# Covers: TCOV-07-005, TCOV-07-013
# Objective: Verify system does not react when student clicks 'Mark all as read'
#            with no notifications.
# ══════════════════════════════════════════════════════════════════════════════
def test_tp_07_004_no_reaction_when_no_notifications(driver):
    login(driver, NO_NOTIF_USER, NO_NOTIF_PASS)

    click_bell(driver)
    time.sleep(1)

    driver.implicitly_wait(0)
    mark_btns = driver.find_elements(By.XPATH, MARK_READ_XPATH)
    driver.implicitly_wait(WAIT_TIMEOUT)

    if mark_btns:
        mark_btns[0].click()
        time.sleep(1)

    assert "dashboard" in driver.current_url.lower(), \
        "System should remain on dashboard when no notifications exist."


# ══════════════════════════════════════════════════════════════════════════════
# TP-07-005 | TC-07-005
# Covers: TCOV-07-006, TCOV-07-007, TCOV-07-008
# Objective: Verify system handles valid and invalid notification states correctly.
#   Test 1 – Valid:   unread notifications displayed and marked as read
#   Test 2 – Invalid: 0 notifications, system does not react
#   Test 3 – Invalid: all already read, mark as read has no effect
# ══════════════════════════════════════════════════════════════════════════════
def test_tp_07_005_system_handles_valid_and_invalid_notification_states(driver):
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # ── Test 1: Valid – unread notifications displayed and marked as read ──────
    login(driver, NOTIF_USER, NOTIF_PASS)
    click_bell(driver)
    mark_btn = wait.until(EC.element_to_be_clickable((By.XPATH, MARK_READ_XPATH)))
    assert mark_btn.is_displayed(), \
        "Test 1: 'Mark all as read' button should be visible when unread notifications exist."
    mark_btn.click()
    time.sleep(1)
    assert "dashboard" in driver.current_url.lower(), \
        "Test 1: Should remain on dashboard after marking notifications as read."

    # ── Test 2: Invalid – 0 notifications, system does not react ─────────────
    login(driver, NO_NOTIF_USER, NO_NOTIF_PASS)
    click_bell(driver)
    time.sleep(1)
    driver.implicitly_wait(0)
    mark_btns_2 = driver.find_elements(By.XPATH, MARK_READ_XPATH)
    driver.implicitly_wait(WAIT_TIMEOUT)
    if mark_btns_2:
        mark_btns_2[0].click()
        time.sleep(1)
    assert "dashboard" in driver.current_url.lower(), \
        "Test 2: System should not react and stay on dashboard when no notifications exist."

    # ── Test 3: Invalid – all already read, mark as read has no effect ────────
    login(driver, NOTIF_USER, NOTIF_PASS)
    driver.refresh()
    wait.until(EC.url_contains("dashboard"))
    time.sleep(1)
    click_bell(driver)
    time.sleep(1)
    driver.implicitly_wait(0)
    mark_btns_3 = driver.find_elements(By.XPATH, MARK_READ_XPATH)
    driver.implicitly_wait(WAIT_TIMEOUT)
    if mark_btns_3:
        mark_btns_3[0].click()
        time.sleep(1)
    assert "dashboard" in driver.current_url.lower(), \
        "Test 3: System should stay on dashboard when all notifications are already read."
