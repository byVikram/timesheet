# 🏏 Dream11 Fantasy Sports Backend API

A scalable Flask backend for a fantasy sports application, featuring player management, team creation, and match simulations.

## 🌟 Features

- RESTful API with Flask-Smorest
- Database operations with SQLAlchemy ORM
- Request/response validation with Marshmallow
- Database migrations with Flask-Migrate
- MySQL database support
- OpenAPI (Swagger) documentation
- Modular architecture with blueprints

## 📦 Project Structure

dream11-backend/
├── app/
│ ├── init.py # Application factory
│ ├── extensions.py # Flask extensions initialization
│ ├── config.py # Configuration settings
│ ├── models/ # Database models
│ │ ├── user.py # User model
│ │ ├── player.py # Player model
│ │ ├── team.py # Team model
│ │ └── ... # Other models
│ ├── routes/ # API blueprints
│ │ ├── users.py # User routes
│ │ ├── players.py # Player routes
│ │ ├── teams.py # Team routes
│ │ └── ... # Other route blueprints
│ ├── schemas/ # Marshmallow schemas
│ ├── services/ # Business logic
│ ├── utils/ # Helper functions
│ └── tests/ # Test cases
├── migrations/ # Database migration files
├── venv/ # Virtual environment (ignored)
├── requirements.txt # Python dependencies
└── main.py # Application entry point

---


## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dream11-backend.git
   cd dream11-backend
   ```

2. **Create and activate virtual environment**
    python -m venv venv
    # Linux/MacOS
    source venv/bin/activate
    # Windows
    venv\Scripts\activate

3. **Install dependencies**
pip install -r requirements.txt

4. **Configure database**

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://username:password@localhost/dream11_dev"

5. **Run database migrations**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

```shell
python -m flask db migrate -m "Initial migration"
```

**

flask run



flask db migrate -m "Describe your change here"
flask db upgrade





