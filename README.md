# FastAPI User Management REST API

A robust and scalable REST API built with FastAPI for user management, featuring secure authentication, a clean architecture, and a containerized setup ready for production.

## ✨ Key Features

- **Modern Tech Stack**: Built with Python 3.12 and **FastAPI** for high performance and asynchronous capabilities.
- **Clean Architecture**: Follows a clear separation of concerns with distinct layers for **Routers**, **Services**, and **Repositories**, making the codebase easy to maintain and extend.
- **Secure Authentication**: Implements JWT-based authentication using secure, **HttpOnly cookies**, protecting against XSS attacks. Passwords are securely hashed using `bcrypt`.
- **Database Management**: Uses **SQLAlchemy ORM** for database interactions and **Alembic** for handling database schema migrations.
- **Dependency Injection**: Leverages FastAPI's powerful dependency injection system to manage dependencies and improve testability.
- **Containerized**: Includes a multi-stage `Dockerfile` for building lightweight, production-ready Docker images, optimized for platforms like **Render**.
- **Comprehensive Testing**: A full suite of unit and integration tests written with **Pytest**, ensuring code reliability.
- **Pagination**: Built-in support for paginating list results.

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

- **Python 3.12+**
- **Poetry** for dependency management.

### Local Development Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/api-rest.git
    cd api-rest
    ```

2.  **Install dependencies using Poetry:**
    ```sh
    poetry install
    ```

3.  **Create an environment file:**
    Create a `.env` file in the root directory by copying the example file. This file will hold your environment variables.
    ```sh
    cp .env.example .env
    ```
    Now, fill in the variables in your new `.env` file:
    ```env
    # Application settings
    SECRET_KEY="your-super-secret-key-for-jwt"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    COOKIE_SECURE=False # Set to True in production with HTTPS

    # Database settings
    DATABASE_URL="postgresql+psycopg2://user:password@localhost/dbname"
    ```

4.  **Run database migrations:**
    Apply the latest database schema using Alembic.
    ```sh
    poetry run alembic upgrade head
    ```

5.  **Run the development server:**
    The application will be available at `http://127.0.0.1:8000`.
    ```sh
    poetry run uvicorn src.main:app --reload
    ```

### Running Tests

To run the entire test suite, use the following command:

```sh
poetry run pytest
```

---

## 📁 Project Structure

The project follows a structured and modular layout:

```
├── alembic/           # Alembic migration scripts
├── src/               # Main application source code
│   ├── core/          # Application configuration (settings)
│   ├── database/      # SQLAlchemy models and session management
│   ├── dependencies/  # FastAPI dependency injection setup
│   ├── repositories/  # Data access layer (interacts with the DB)
│   ├── routers/       # API endpoint definitions
│   ├── schemas/       # Pydantic models for data validation (DTOs)
│   └── services/      # Business logic layer
├── tests/             # Unit and integration tests
├── .env.example       # Example environment variables file
├── alembic.ini        # Alembic configuration
├── Dockerfile         # Container definition for deployment
└── pyproject.toml     # Project metadata and dependencies (Poetry)
```

---

## Endpoints

Here is a summary of the available API endpoints.

### Authentication

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Log in and receive an authentication cookie.
- `POST /auth/logout`: Log out and clear the authentication cookie.

### Users

- `GET /users/me`: Get details for the currently authenticated user.
- `GET /users`: Get a paginated list of all users.
- `GET /users/{id}`: Get details for a specific user by their ID.

---

## 🐳 Deployment

This application is ready to be deployed as a Docker container. The included `Dockerfile` is optimized for production and works seamlessly with hosting platforms like **Render**, Heroku, or any cloud provider that supports Docker containers.

The server is configured to run on the port specified by the `PORT` environment variable, which is standard for most hosting platforms.

## Resources

Dataset link: https://www.kaggle.com/datasets/carrie1/ecommerce-data?resource=download 