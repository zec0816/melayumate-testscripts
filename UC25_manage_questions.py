import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# Basic configuration
# =========================

BASE_URL = "http://localhost:3001"
LECTURER_USERNAME = "admin"
LECTURER_PASSWORD = "Admin1234*"


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def wait(driver, seconds=10):
    return WebDriverWait(driver, seconds)


# =========================
# Common helper functions
# =========================

def lecturer_login(driver):
    """
    Login as lecturer.
    Lecturer login form uses name='username' for username,
    placeholder='Password' for password, and button text 'Sign In'.
    """
    driver.get(BASE_URL)

    wait(driver).until(
        EC.element_to_be_clickable((By.NAME, "username"))
    ).send_keys(LECTURER_USERNAME)

    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Password']"))
    ).send_keys(LECTURER_PASSWORD)

    sign_in_button = wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
    )

    driver.execute_script("arguments[0].click();", sign_in_button)

    wait(driver).until(EC.url_contains("dashboard"))


    """
    Open lecturer dashboard and select an existing lesson.
    Adjust the URL or locator if your actual lesson page route is different.
    """
def open_existing_lesson(driver):
    driver.get(BASE_URL + "/dashboard")

    lesson_card = wait(driver).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(., 'Questions') or contains(., 'Lesson')][contains(@class,'cursor-pointer')]")
        )
    )
    driver.execute_script("arguments[0].click();", lesson_card)

    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Multiple Choices')]"))
    )

def select_question_type(driver, question_type):
    """
    Select a question type.
    Available labels:
    - Multiple Choices
    - Sentence Building
    - Listening
    """
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),'{question_type}')]"))
    ).click()


def assert_message(driver, message):
    wait(driver).until(
        EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(),'{message}')]"))
    )


def click_delete_first_question(driver):
    """
    Delete the first available question.
    QuestionList uses icon buttons with title='Delete Question'.
    """
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "(//button[@title='Delete Question'])[1]"))
    ).click()


def click_analytics_first_question(driver):
    """
    Open analytics for the first available question.
    QuestionList uses icon buttons with title='View Analytics'.
    """
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "(//button[@title='View Analytics'])[1]"))
    ).click()


# =========================
# Multiple Choice helpers
# =========================


    """
    Multiple Choice starts with 4 options.
    Remove options until the target option count is reached.
    """
def remove_option_until_count(driver, target_count):
    while True:
        option_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Option #')]")
        if len(option_inputs) <= target_count:
            break

        # click the trash button beside the last option input only
        last_option = option_inputs[-1]
        remove_button = last_option.find_element(
            By.XPATH,
            "./following-sibling::button"
        )
        driver.execute_script("arguments[0].click();", remove_button)
        time.sleep(0.3)

def remove_word_until_count(driver, target_count):
    while True:
        word_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")
        if len(word_inputs) <= target_count:
            break

        last_word = word_inputs[-1]
        remove_button = last_word.find_element(
            By.XPATH,
            "./following-sibling::button"
        )
        driver.execute_script("arguments[0].click();", remove_button)
        time.sleep(0.3)

def fill_multiple_choice(driver, prompt, options, correct_index=0):
    """
    Fill Multiple Choice form.
    Min 2 options, max 4 options.
    """
    prompt_input = wait(driver).until(
        EC.element_to_be_clickable((By.ID, "promptText"))
    )
    prompt_input.clear()
    prompt_input.send_keys(prompt)

    remove_option_until_count(driver, len(options))

    option_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Option #')]")

    for i, option_text in enumerate(options):
        option_inputs[i].clear()
        option_inputs[i].send_keys(option_text)

    radio_buttons = driver.find_elements(By.XPATH, "//input[@name='correct-answer']")
    radio_buttons[correct_index].click()


def save_multiple_choice(driver):
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save Multiple Choice Question')]"))
    ).click()


# =========================
# Sentence Building helpers
# =========================

def fill_sentence_building(driver, sentence, words, correct_sentence):
    """
    Fill Sentence Building form.
    Form starts with 3 word inputs.
    Allowed boundary: min 2 words, max 8 words.
    """
    sentence_input = wait(driver).until(
        EC.element_to_be_clickable((By.ID, "sentence"))
    )
    sentence_input.clear()
    sentence_input.send_keys(sentence)

    # Adjust word input count
    while len(driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")) < len(words):
        driver.find_element(By.XPATH, "//button[contains(text(),'Add Word')]").click()
        time.sleep(0.2)

    while len(driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")) > len(words):
        remove_word_until_count(driver, len(words))
        time.sleep(0.2)

    word_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")

    for i, word in enumerate(words):
        word_inputs[i].clear()
        word_inputs[i].send_keys(word)

    correct_input = driver.find_element(By.ID, "correctSentence")
    correct_input.clear()
    correct_input.send_keys(correct_sentence)


def save_sentence_building(driver):
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Save Sentence Building Question')]"))
    ).click()


# =========================================================
# TP-25-001
# Objective:
# Verify lecturer can access lesson overview and create a question successfully.
# Test Cases:
# TC-25-001: Access lesson overview
# TC-25-002: Select a question type
# TC-25-003: Create question successfully
# =========================================================

def test_tp_25_001_access_lesson_and_create_question(driver):
    # TC-25-001: Lecturer accesses existing lesson overview
    lecturer_login(driver)
    open_existing_lesson(driver)

    # TC-25-002: Lecturer selects Multiple Choices question type
    select_question_type(driver, "Multiple Choices")

    # TC-25-003: Lecturer creates a valid Multiple Choice question
    fill_multiple_choice(
        driver,
        prompt="What is chicken in Malay?",
        options=["Ayam", "Ikan", "Nasi", "Air"],
        correct_index=0
    )

    save_multiple_choice(driver)

    assert_message(driver, "Question submitted successfully!")


# =========================================================
# TP-25-002
# Objective:
# Verify lecturer can delete a question and proceed to question analytics.
# Test Cases:
# TC-25-004: Delete a question
# TC-25-005: Proceed to question analytics
# =========================================================

def test_tp_25_002_delete_question_and_view_analytics(driver):
    lecturer_login(driver)
    open_existing_lesson(driver)

    # Make sure questions are visible first
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'View Questions')]"))
    ).click()

    # TC-25-005: View question analytics first
    click_analytics_first_question(driver)

    wait(driver).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Question Analytics')]"))
    )

    # Close analytics modal
    wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'×') or contains(text(),'x')]"))
    ).click()

    # TC-25-004: Delete an existing question after viewing analytics
    click_delete_first_question(driver)

    assert_message(driver, "Question deleted.")


# =========================================================
# TP-25-003
# Objective:
# Verify system rejects incomplete question details.
# Test Cases:
# TC-25-006: Incomplete question details
# =========================================================

def test_tp_25_003_reject_incomplete_question_details(driver):
    # TC-25-006: System rejects incomplete required fields
    lecturer_login(driver)
    open_existing_lesson(driver)

    select_question_type(driver, "Multiple Choices")

    # Try to save without filling prompt/options/correct answer
    save_multiple_choice(driver)

    assert_message(driver, "Please provide a prompt text.")


# =========================================================
# TP-25-004
# Objective:
# Verify system handles answer option count boundary values correctly.
# Test Cases:
# TC-25-007: Option count boundary values: 1, 2, 3, 4, 5
# =========================================================

@pytest.mark.parametrize(
    "option_count, expected_result",
    [
        (1, "reject"),
        (2, "accept"),
        (3, "accept"),
        (4, "accept"),
        (5, "reject"),
    ]
)

def test_tp_25_004_answer_option_count_boundary(driver, option_count, expected_result):
    lecturer_login(driver)
    open_existing_lesson(driver)
    select_question_type(driver, "Multiple Choices")

    if option_count == 1:
        # UI should reject deleting below 2 options
        remove_option_until_count(driver, 2)

        option_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Option #')]")
        last_option = option_inputs[-1]
        remove_button = last_option.find_element(By.XPATH, "./following-sibling::button")
        driver.execute_script("arguments[0].click();", remove_button)

        assert_message(driver, "At least 2 options are required.")
        return

    if option_count == 5:
        add_option_button = wait(driver).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Add Option')]"))
        )
        add_option_button.click()
        assert_message(driver, "Maximum of 4 options allowed.")
        return

    options = [f"Option {i}" for i in range(1, option_count + 1)]

    fill_multiple_choice(
        driver,
        prompt=f"Boundary test with {option_count} options",
        options=options,
        correct_index=0
    )

    save_multiple_choice(driver)
    assert_message(driver, "Question submitted successfully!")

    
# =========================================================
# TP-25-005
# Objective:
# Verify system handles Sentence Building word count boundary values correctly.
# Test Cases:
# TC-25-008: Word count boundary values: 1, 2, 3, 8, 9
# =========================================================

@pytest.mark.parametrize(
    "word_count, expected_result",
    [
        (1, "reject"),
        (2, "accept"),
        (3, "accept"),
        (8, "accept"),
        (9, "reject"),
    ]
)
def test_tp_25_005_sentence_building_word_count_boundary(driver, word_count, expected_result):
    # TC-25-008: Check Sentence Building word count boundary
    lecturer_login(driver)
    open_existing_lesson(driver)

    select_question_type(driver, "Sentence Building")

    if word_count == 9:
        # UI max is 8. Attempt to add 9th word should show error.
        while len(driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")) < 8:
            driver.find_element(By.XPATH, "//button[contains(text(),'Add Word')]").click()
            time.sleep(0.2)

        driver.find_element(By.XPATH, "//button[contains(text(),'Add Word')]").click()
        assert_message(driver, "Maximum of 8 words allowed.")
        return

    if word_count == 1:
      # UI should reject deleting below 2 words
      remove_word_until_count(driver, 2)

      word_inputs = driver.find_elements(By.XPATH, "//input[starts-with(@placeholder,'Word #')]")
      last_word = word_inputs[-1]
      remove_button = last_word.find_element(By.XPATH, "./following-sibling::button")
      driver.execute_script("arguments[0].click();", remove_button)

      assert_message(driver, "At least two words are required.")
      return

    words = [f"word{i}" for i in range(1, word_count + 1)]

    fill_sentence_building(
        driver,
        sentence=f"Arrange {word_count} words",
        words=words,
        correct_sentence=" ".join(words)
    )

    save_sentence_building(driver)

    if expected_result == "accept":
        assert_message(driver, "Question submitted successfully!")
        