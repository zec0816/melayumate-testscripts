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

| Use Case | Description             |
| -------- | ----------------------- |
| UC01     | Login                   |
| UC02     | Register Account        |
| UC03     | Reset Password          |
| UC04     | Edit Profile            |
| UC05     | Manage Drone & Location |
| UC06     | Manage Drone Images     |
| UC07     | Manage User             |
| UC08     | Manage Dengue Data      |
| UC09     | Manage Weather Data     |
| UC10     | Generate Report         |
| UC12     | Manage Settings         |
| UC13     | Get Dengue Notification |

---

# Notes

* Ensure ChromeDriver version matches the installed browser version.
* Ensure all required services are running before executing tests.
* Some test scripts require stable backend connectivity.
* Test scripts use predefined testing accounts and sample data.