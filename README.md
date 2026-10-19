# KanMind Backend

KanMind is a REST API backend for a Kanban-based task management application, developed with Django and Django REST Framework.

Users can register, log in, create boards, manage tasks, assign users, and add comments. Token-based authentication and permissions protect access to the application's resources.

## How to Install

### 1. Create a Virtual Environment

**Unix / macOS**

```bash
python3 -m venv .venv
```

**Windows**

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment

**Unix / macOS**

```bash
source .venv/bin/activate
```

**Windows (CMD)**

```bash
.venv\Scripts\activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

**Unix / macOS**

```bash
python3 -m pip install -r requirements.txt
```

**Windows**

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory, next to `manage.py`.

Use `.env_Template` as a reference:

```env
SECRET_KEY=your_generated_django_secret_key
DEBUG=True
```

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the generated key into your `.env` file.

The `.env` file must not be committed to Git.

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the terminal instructions to create an administrator account.

### 7. Start the Development Server

```bash
python manage.py runserver
```

The server runs at:

`http://127.0.0.1:8000/`

Django Admin:

`http://127.0.0.1:8000/admin/`

## Tech Stack

- Python
- Django
- Django REST Framework (DRF)
- SQLite
- Django REST Framework Token Authentication
- python-dotenv

## Authentication

KanMind uses token-based authentication.

After registration or login, the API returns an authentication token.

Protected endpoints require the following HTTP header:

```http
Authorization: Token YOUR_AUTH_TOKEN
```

Registration and login are publicly accessible. All other API endpoints require authentication.

## API Routes

Base URL: `http://127.0.0.1:8000/api/`

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Log in and receive an authentication token |

### Boards

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/boards/` | List accessible boards |
| POST | `/api/boards/` | Create a new board |
| GET | `/api/boards/{board_id}/` | Retrieve board details |
| PATCH | `/api/boards/{board_id}/` | Update a board |
| DELETE | `/api/boards/{board_id}/` | Delete a board |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/tasks/` | Create a task |
| PATCH | `/api/tasks/{task_id}/` | Update a task |
| DELETE | `/api/tasks/{task_id}/` | Delete a task |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | List tasks reviewed by the current user |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/{task_id}/comments/` | List task comments |
| POST | `/api/tasks/{task_id}/comments/` | Create a task comment |
| DELETE | `/api/tasks/{task_id}/comments/{comment_id}/` | Delete a comment |

### Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/email-check/?email={email}` | Find a user by email address |

## Permissions

- Only authenticated users can access protected endpoints.
- Board owners and members can view their boards.
- Only board owners can update or delete boards.
- Board owners and members can create and update tasks.
- Only task creators or board owners can delete tasks.
- Assignees and reviewers must belong to the corresponding board or be its owner.
- Board owners and members can view and create task comments.
- Only comment authors can delete their comments.

## Project Structure

```text
Pascal-KanMind/
├── auth_App/
│   └── api/
│       ├── serializers.py
│       ├── urls.py
│       └── views.py
├── kanban_App/
│   ├── api/
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── migrations/
│   ├── admin.py
│   └── models.py
├── core/
│   ├── settings.py
│   └── urls.py
├── .env_Template
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Database

The project uses SQLite for local development.

The database is created automatically when migrations are applied.

The `db.sqlite3` file is excluded from Git.

## Development Checks

Check the Django configuration:

```bash
python manage.py check
```

Check for missing model migrations:

```bash
python manage.py makemigrations --check --dry-run
```

## Notes

- This repository contains the backend application only.
- Environment variables are loaded from `.env`.
- The `.env` file and local database are excluded from version control.
- The API can be tested using Postman or another HTTP client.