# FastAPI Ecommerce Data Analysis API

A robust and scalable REST API built with FastAPI for e-commerce data analytics/analysis. It includes secure authentication, background tasks with Celery, high-performance caching with Redis, and a clean, production-ready architecture.

## ✨ Key Features

- **Modern Tech Stack**: Built with Python 3.12 and **FastAPI** for high performance and asynchronous capabilities.
- **Clean Architecture**: Follows a clear separation of concerns with distinct layers for **Routers**, **Services**, and **Repositories**, making the codebase easy to maintain and extend.
- **Secure Authentication**: Implements JWT-based authentication using secure **HttpOnly cookies** to protect against XSS attacks. Passwords are securely hashed using `bcrypt`.
- **Database Management**: Uses **SQLAlchemy ORM** for database interactions and **Alembic** for handling database schema migrations.
- **Asynchronous Background Tasks**: Utilizes **Celery** with a **Redis** broker to run tasks in the background, like pre-calentando el caché de datos.
- **Performance Caching**: Implements a caching layer with **Redis** to store expensive computations (like DataFrames de Pandas) and API responses, drastically reducing response times.
- **Data Analysis & Metrics**: Provides endpoints for analyzing e-commerce data, calculating KPIs, generating time series, and identifying top-performing countries.
- **Dependency Injection**: Leverages FastAPI's powerful dependency injection system to manage dependencies and improve testability.
- **Developer Tooling**: Uses **`poethepoet`** and **`honcho`** to simplify the local development workflow, allowing you to start the entire application stack (API, worker, scheduler) with a single command.
- **Containerized**: Includes a multi-stage `Dockerfile` for building lightweight, production-ready Docker images, optimized for platforms like **Render**.
- **Comprehensive Testing**: A full suite of unit and integration tests written with **Pytest**, ensuring code reliability.

---

## 🚀 Puesta en Marcha

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

5.  **Run the entire development environment:**
    This single command will automatically:
    - Kill any processes lingering on port 8000.
    - Start the FastAPI server (`uvicorn`).
    - Start the Celery worker to process tasks.
    - Start the Celery beat scheduler to queue periodic tasks.
    
    The application will be available at `http://127.0.0.1:8000`.
    ```sh
    poetry run poe dev:all
    ```

### Development Helper Scripts

The `pyproject.toml` file contains several useful scripts managed by `poethepoet`:

- `poe dev`: Starts only the FastAPI server with auto-reload.
- `poe worker`: Starts only the Celery worker.
- `poe beat`: Starts only the Celery beat scheduler.
- `poe kill`: Kills any process running on port 8000.
- `poe kill:celery`: Finds and forcefully terminates all lingering Celery processes.
- `poe dev:all`: Kills old processes and starts the complete environment (server + worker + beat).

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

### Metrics & Data Analysis

- `GET /metrics/kpis`: Get a summary of Key Performance Indicators (total revenue, etc.).
- `GET /metrics/series`: Get time series data for revenue and products sold (daily, weekly, monthly, yearly).
- `GET /metrics/top-countries`: Get a list of top countries by revenue or products sold.
- `GET /metrics/top-countries/{country_name}`: Get detailed metrics for a specific country.
- `GET /metrics/page`: Get a paginated view of the raw, cleaned transaction data.

## 🐳 Deployment

This application is ready to be deployed as a Docker container. The included `Dockerfile` is optimized for production and works seamlessly with hosting platforms like **Render**, Heroku, or any cloud provider that supports Docker containers.

The server is configured to run on the port specified by the `PORT` environment variable, which is standard for most hosting platforms.

## Resources

Dataset link: https://www.kaggle.com/datasets/carrie1/ecommerce-data?resource=download 
