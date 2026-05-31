# MelayuMate Test Scripts

This repository contains automated test scripts for the **MelayuMate** system using:

- Selenium (Web Testing)
- Pytest (Test Framework)

---

# Prerequisites

Make sure the following are installed:

- Python 3.10+
- ChromeDriver
- Node.js
- MySQL Server
- Java 17+
- Maven

---

# Clone Repository

```bash
git clone https://github.com/zec0816/melayumate-testscripts.git
cd melayumate-testscripts
````

---

# Install Required Packages

```bash
pip install pytest selenium webdriver-manager
```

---

# Start Required Services

Before running the test scripts, ensure the following are running:

- MelayuMate Student Frontend
- MelayuMate Lecturer Frontend
- MelayuMate Spring Boot Backend
- MelayuMate AI Service
- MySQL Database

---

# Run Test Scripts

## Run All Tests

```bash
pytest
```

---

## Run Individual Tests

```bash
pytest test_uc01_login_web.py
pytest test_uc01_login_mobile.py
pytest test_uc02_register_account_web.py
pytest test_uc02_register_account_mobile.py
```

---

# Current Test Coverage

| Use Case | Description |
|----------|-------------|
| UC01 | Register Account |
| UC02 | Login |
| UC03 | Reset Password |
| UC04 | View Daily Progress |
| UC05 | View Level Progress |
| UC06 | Manage Daily Goal |
| UC07 | Manage Notifications |
| UC08 | Chat with Peers |
| UC09 | Unlock Character |
| UC10 | Manage Character Settings |
| UC11 | Manage Battle Availability |
| UC12 | Battle Opponent |
| UC13 | Manage Deck |
| UC14 | Manage Card |
| UC15 | Configure Deck Settings |
| UC16 | Practice Card |
| UC17 | Manage Scenario |
| UC18 | Manage Dialogue |
| UC19 | Generate Audio (TTS) |
| UC20 | Transcribe Speech (STT) |
| UC21 | Practice Dialogue |
| UC22 | Practice Lesson |
| UC23 | Review Completed Lesson |
| UC24 | Manage Lessons |
| UC25 | Manage Questions |
| UC26 | View Analytics |

---

# Notes

* Ensure ChromeDriver version matches the installed browser version.
* Ensure all required services are running before executing tests.
* Some test scripts require stable backend connectivity.
* Test scripts use predefined testing accounts and sample data.