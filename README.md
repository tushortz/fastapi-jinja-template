# [Project name]

A FastAPI-based web application starter temmplate supporting mongodb backend and ttailwind css

## Features

-   **User Authentication**: Registration and login with JWT tokens
-   **Admin Panel**: Manage users and view system statistics
-   **Responsive UI**: Modern, mobile-friendly interface using Tailwind CSS

## Tech Stack

-   **Backend**: FastAPI, Python 3.11+
-   **Database**: MongoDB with Motor (async driver)
-   **Authentication**: JWT tokens with bcrypt password hashing
-   **Frontend**: Jinja2 templates with Alpine.js and Tailwind CSS
-   **Testing**: pytest with async support
-   **Code Quality**: ruff and black for formatting

## Project Structure

```
project-template/
├── env/                          # Virtual environment
├── src/                          # Main application source code
│   ├── api/                      # API endpoints
│   │   ├── admin.py             # Admin API routes
│   │   ├── auth.py              # Authentication API routes
│   │   └── image_converter.py   # Image conversion API
│   ├── models/                   # Database models
│   │   ├── base.py              # Base model class
│   │   └── users.py             # User model
│   ├── repositories/             # Data access layer
│   │   ├── base.py              # Base repository class
│   │   └── users.py             # User repository
│   ├── services/                 # Business logic layer
│   │   ├── users.py             # User service
│   │   └── tagging/             # Tagging services
│   │       ├── base.py          # Base tagging service
│   │       ├── gemini.py        # Gemini AI tagging
│   │       └── local_ai.py      # Local AI tagging
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── admin/               # Admin panel templates
│   │   │   ├── dashboard.html
│   │   │   └── users.html
│   │   ├── auth/                # Authentication templates
│   │   │   ├── login.html
│   │   │   ├── profile.html
│   │   │   └── register.html
│   │   ├── components/          # Reusable components
│   │   │   └── modal.html
│   │   ├── dashboard/           # Dashboard templates
│   │   │   └── dashboard.html
│   │   ├── base.html            # Base template
│   │   └── landing.html         # Landing page
│   ├── tests/                    # Test suite
│   │   ├── factories/           # Test data factories
│   │   │   ├── base.py
│   │   │   └── user.py
│   │   ├── conftest.py          # Pytest configuration
│   │   ├── test_api.py          # API tests
│   │   ├── test_models.py       # Model tests
│   │   ├── test_repositories.py # Repository tests
│   │   └── test_services.py     # Service tests
│   ├── static/                   # Static assets
│   │   └── css/
│   │       └── custom.css       # Custom CSS styles
│   ├── utils/                    # Utility functions
│   │   └── date.py              # Date utilities
│   ├── auth.py                   # Authentication utilities
│   ├── config.py                 # Application configuration
│   ├── database.py               # Database connection
│   ├── main.py                   # FastAPI application entry point
│   ├── scripts.py                # Utility scripts
│   └── web_routes.py             # Web route handlers
├── env.example                   # Environment variables template
├── poetry.lock                   # Poetry lock file
├── pyproject.toml               # Project configuration
└── README.md                     # Project documentation
```


## Installation

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd <repo>
    ```

2. **Install Poetry** (if not already installed):

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install dependencies**:

    ```bash
    poetry install
    ```

4. **Set up MongoDB**:

    - Install MongoDB locally or use MongoDB Atlas
    - Update the connection string in `config.py` if needed

5. **Configure environment variables**:

    - Copy `.env.example` to `.env` and update the values
    - Set a strong `SECRET_KEY` for JWT token signing

6. **Run the application**:

    ```bash
    poetry run dev
    ```

    The application will be available at `http://localhost:8000`

## Usage

### User Registration and Login

1. Visit the application in your browser
2. Click "Register" to create a new account
3. Fill in your email, username, and password
4. Log in with your credentials

### Admin Features

Admin users can:

-   View system statistics
-   Manage all users
-   Access the admin dashboard

## API Documentation

Once the application is running, you can access the interactive API documentation at:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Testing

Run the test suite:

```bash
# Run all tests
poetry run test

# Run with coverage
poetry run pytest --cov=.

# Run specific test file
poetry run pytest src/tests/test_{file}.py
```

## Code Quality

The project uses ruff and black for code formatting and linting:

```bash
# Format code
poetry run format

# Lint code
poetry run lint

# Fix linting issues
poetry run lint-fix
```

## Configuration

Key configuration options in `src/config.py`:

-   `MONGODB_URL`: MongoDB connection string
-   `DATABASE_NAME`: Database name
-   `SECRET_KEY`: JWT signing key
-   `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Security Features

-   Password hashing with bcrypt
-   JWT token authentication
-   User input validation
-   SQL injection prevention (MongoDB)
-   CORS configuration
-   Admin role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.
