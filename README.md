# [Project name]

A FastAPI-based web application for saving and managing quotes from books. Built with MongoDB as the backend database and featuring a modern web UI.

## Features

-   **User Authentication**: Registration and login with JWT tokens
-   **Search Functionality**: Find quotes and books quickly
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

```

## Installation

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd quote
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
