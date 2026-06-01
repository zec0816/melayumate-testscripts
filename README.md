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
pytest test_uc06_manage_daily_goal.py
pytest test_uc07_manage_notifications.py
pytest test_uc10_manage_character_settings.py
pytest test_uc24_manage_lessons.py
```

---

# Current Test Coverage

| Use Case | Description |
|----------|-------------|
| UC06 | Manage Daily Goal |
| UC07 | Manage Notifications |
| UC10 | Manage Character Settings |
| UC13 | Manage Deck |
| UC15 | Configure Deck Settings |
| UC24 | Manage Lessons |

---

# Notes

* Ensure ChromeDriver version matches the installed browser version.
* Ensure all required services are running before executing tests.
* Some test scripts require stable backend connectivity.
* Test scripts use predefined testing accounts and sample data.
