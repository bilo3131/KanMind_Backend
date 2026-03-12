# KanMind Backend

REST API for KanMind – a Kanban board application. Built with Django and Django REST Framework.

## Tech Stack

- Python 3.x
- Django 5.2
- Django REST Framework 3.16
- django-cors-headers
- SQLite (development)

## Setup

**1. Clone the repository and navigate to the backend folder:**

```bash
cd Backend
```

**2. Create and activate a virtual environment:**

```bash
python -m venv env
# Windows
env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Apply migrations:**

```bash
python manage.py migrate
```

**5. Start the development server:**

```bash
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/api/`.

## API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/registration/` | Register a new user |
| POST | `/api/login/` | Login and receive token |
| GET | `/api/email-check/` | Check if email is already in use |

### User Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles/` | List all user profiles |
| GET/PATCH/DELETE | `/api/profiles/<id>/` | Retrieve, update or delete a profile |

### Boards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/boards/` | List all boards or create a new one |
| GET/PATCH/DELETE | `/api/boards/<id>/` | Retrieve, update or delete a board |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/tasks/` | List all tasks or create a new one |
| GET/PATCH/DELETE | `/api/tasks/<id>/` | Retrieve, update or delete a task |
| GET | `/api/tasks/assigned-to-me/` | Tasks assigned to the current user |
| GET | `/api/tasks/reviewing/` | Tasks where the current user is reviewer |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/tasks/<task_id>/comments/` | List or create comments for a task |
| GET/PATCH/DELETE | `/api/tasks/<task_id>/comments/<id>/` | Retrieve, update or delete a comment |

## Data Models

- **UserProfile** – extends Django's built-in User with a `fullname` field
- **Board** – has a title, an owner, and multiple members
- **Task** – belongs to a board, has a title, description, priority (`low`, `medium`, `high`), status (`to-do`, `in-progress`, `review`, `done`), assignee, reviewer, and due date
- **Comment** – belongs to a task, has an author, content, and timestamp

## Project Structure

```
Backend/
├── kanmind_backend/     # Django project settings & URL config
├── kanmind_app/         # Boards, Tasks, Comments
│   ├── api/             # Serializers, Views, URLs
│   └── models.py
├── auth_user/           # User registration & authentication
│   ├── api/             # Serializers, Views
│   └── models.py
├── manage.py
└── requirements.txt
```
