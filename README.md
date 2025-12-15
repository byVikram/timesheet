# Timesheets Backend API

A scalable Flask backend for managing timesheets.

---

## 🌟 Features

- RESTful API with Flask-Smorest
- Database operations with SQLAlchemy ORM
- Request/response validation with Marshmallow
- Database migrations with Flask-Migrate
- MySQL database support
- OpenAPI (Swagger) documentation
- Modular architecture with blueprints

---

## 📦 Project Structure


```
timesheet/
├── app/
│ ├── constants/ # Project-wide constants
│ ├── models/ # Database models
│ ├── routes/ # API routes / endpoints
│ ├── schemas/ # Pydantic schemas / validation
│ ├── services/ # Business logic and services
│ ├── utils/ # Utility functions
│ └── pycache/ # Python cache files
├── logs/ # Log files
├── migrations/ # Database migrations
│ └── versions/ # Migration versions
├── tests/ # Unit and integration tests
└── .venv/ # Python virtual environment (ignored)
```
---


## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip

---

### Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/timesheet.git
    cd timesheet
    ```


2. **Create and activate virtual environment**
    ## Create virtual environment
    ```
    python -m venv .venv
    ```

    ## Activate virtual environment
    ### Windows
    ```
    .venv\Scripts\activate
    ```
    ### Linux / macOS
    ```
    source .venv/bin/activate
    ```


3. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```


4. **Configure database**

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://username:password@localhost/timesheet"


5. **Run database migrations**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

    ```shell
    python -m flask db migrate -m "Initial migration"
    ```

6. **Run Apllication**
    flask run




