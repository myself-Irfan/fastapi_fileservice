## Document Manager

A **FastAPI**-based document and file management application with a server-rendered frontend.

---

## Features

- User registration & login with **JWT authentication** (access + refresh tokens)
- **Document Collections** — create, read, update, and delete collections
- **File Management** — upload, download, and delete files with SHA-256 deduplication and MIME-type validation
- Files can be linked to a collection or kept standalone
- Soft delete for files with conditional physical removal (only removes from disk when no other record shares the same checksum)
- **Rate limiting** on registration
- Structured logging with per-request context and sensitive data masking
- Server-rendered frontend (Jinja2 + Bootstrap 5 + Vanilla JS)
- Dockerized for local development and deployment
- CI with automated tests

---

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Jinja2 templates, Bootstrap 5, Vanilla JS
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (HS256)
- **File type validation**: python-magic
- **Testing**: pytest
- **Containerization**: Docker, Docker Compose
- **CI**: GitHub Actions

---

## Architecture

The app is split into four domain modules under `app/`:

| Module | Responsibility |
|--------|---------------|
| `auth` | JWT issue and validation |
| `userapp` | Registration, login, user views |
| `collectionapp` | CRUD for document collections |
| `fileapp` | Upload, download, delete, and listing of files |

Each module follows a strict layer structure: **Router → Service → Entity → Model**, with domain-specific exceptions and FastAPI `Depends()` wiring.

All domain exceptions share a common `AppException` base (`app/exceptions.py`) and are converted to HTTP responses by a single global exception handler (`app/exception_handler.py`) — routers never catch and translate errors themselves.

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/users/register` | Register a new user |
| `POST` | `/api/users/login` | Login and receive tokens |
| `POST` | `/api/auth/refresh-token` | Refresh access token |
| `GET` | `/api/collection/` | List all collections |
| `POST` | `/api/collection/` | Create a collection |
| `GET` | `/api/collection/{id}` | Get a collection |
| `PUT` | `/api/collection/{id}` | Update a collection |
| `DELETE` | `/api/collection/{id}` | Delete a collection |
| `GET` | `/api/files/` | List all files (filter by `document_id`) |
| `GET` | `/api/files/{id}` | Get file metadata |
| `DELETE` | `/api/files/{id}` | Soft-delete a file |
| `POST` | `/api/files/upload` | Upload a file |
| `GET` | `/api/files/{id}/download` | Download a file |

Interactive API docs are available once the app is running:

| UI | URL |
|----|-----|
| Swagger UI | `http://localhost:8080/docs` |
| ReDoc | `http://localhost:8080/redoc` |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/myself-Irfan/fastapi_todoapp.git
cd fastapi_todoapp
```

### 2. Set up environment variables

Copy `sample.env` to `.env` and fill in the values.

Key variables:

```env
# Database
DB_USER=...
DB_PWD=...
DB_HOST=localhost        # use host.docker.internal for Docker
DB_PORT=5432
DB_NAME=...

# Auth
SECRET_KEY=...
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# File uploads
UPLOAD_DIR=uploads/
ALLOWED_FILE_TYPES=.pdf,.png,.jpg,.jpeg,.txt,.csv

# Rate limiting
REGISTER_LIMIT_PER_HOUR=5

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs/
LOG_FILE=app.log
MASKING_KEYS=password,hashed_pwd,token
```

### 3. Run the application

**Local:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**Docker:**
```bash
docker compose up --build -d
```

### 4. Run tests

**Local:**
```bash
pytest -v
```

**Docker:**
```bash
docker compose run --rm web pytest -v
```

Run only a specific domain:
```bash
pytest -m fileapp -v
pytest -m collectionapp -v
pytest -m userapp -v
```

---

## CI/CD

- GitHub Actions run the full test suite on every push and pull request to `master`
- A PostgreSQL service container is spun up for integration tests
- Environment variables are provided via CI secrets / hardcoded dummies

---

## Logging

Logs are written to the directory set by `LOG_DIR`. Each request is logged with a unique request ID, user context (where available), and sensitive fields (configured via `MASKING_KEYS`) are automatically redacted.

---

## License

Copyright (c) 2025 Irfan Ahmed