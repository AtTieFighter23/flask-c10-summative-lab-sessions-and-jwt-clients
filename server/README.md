# Full Auth Flask Backend — Notes App

A secure RESTful Flask API backend supporting user authentication (session-based)
and full CRUD operations on a user-owned Notes resource. Built as the summative
project for Course 10 (Cookies/Sessions/Auth + Data Structures unit).

## Project Description

This API allows users to sign up, log in, and manage their own personal notes.
Each user can only view, create, update, or delete their own notes — no user can
access another user's data. Passwords are securely hashed using bcrypt, and
sessions are used to persist login state across requests.

Built to work with the provided `client-with-sessions` React frontend.

## Tech Stack

- Flask 2.2.2
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 4.0.0
- Flask-RESTful 0.3.9
- Flask-Bcrypt 1.0.1
- Marshmallow 3.20.1
- Faker 15.3.2 (for seeding)
- SQLite

## Installation

From the `server/` directory:

```bash
pipenv install
pipenv shell
```

Set the Flask app environment variable:

```bash
export FLASK_APP=app.py
```

## Database Setup

Run migrations to create the database schema:

```bash
flask db upgrade head
```

Seed the database with example users and notes:

```bash
python seed.py
```

This creates 5 example users (password: `password123` for all) and 3 notes each.

## Running the Server

```bash
python app.py
```

The API will run on `http://localhost:5555`, matching the proxy configuration
in the provided React client (`client-with-sessions`).

To run the full app alongside the frontend, in a separate terminal:

```bash
cd ../client-with-sessions
npm install
npm start
```

The client will open on `http://localhost:4000`.

## API Endpoints

### Auth

| Method | Endpoint         | Description                                  | Auth Required |
|--------|------------------|-----------------------------------------------|----------------|
| POST   | `/signup`        | Create a new user account and log in         | No             |
| POST   | `/login`         | Log in an existing user                       | No             |
| DELETE | `/logout`        | Log out the current user                      | Yes            |
| GET    | `/check_session` | Check if a user is currently logged in        | Yes            |

**Signup body:** `{ "username": "...", "password": "...", "password_confirmation": "..." }`
**Login body:** `{ "username": "...", "password": "..." }`

### Notes

| Method | Endpoint       | Description                                | Auth Required |
|--------|----------------|---------------------------------------------|----------------|
| GET    | `/notes`       | Get a paginated list of the user's notes    | Yes            |
| POST   | `/notes`       | Create a new note                            | Yes            |
| GET    | `/notes/<id>`  | Get a single note (must be owned by user)    | Yes            |
| PATCH  | `/notes/<id>`  | Update a note (must be owned by user)        | Yes            |
| DELETE | `/notes/<id>`  | Delete a note (must be owned by user)        | Yes            |

**Note body (create/update):** `{ "title": "...", "content": "..." }`

**Pagination query params (on GET /notes):** `?page=1&per_page=10`

## Authentication & Authorization

- Passwords are hashed using Flask-Bcrypt and never stored or returned in plain text.
- Sessions are used to track logged-in users via a secure cookie.
- All Notes routes check for an active session and verify that the requesting
  user owns the note before allowing read/update/delete access. Attempting to
  access another user's note returns a `404`. Accessing any protected route
  without a valid session returns a `401`.

## Project Structure

```
server/
├── app.py          # Route definitions (Flask-RESTful resources)
├── config.py        # App, database, and extension configuration
├── models.py        # SQLAlchemy models (User, Note)
├── schemas.py        # Marshmallow serialization schemas
├── seed.py          # Database seeding script
├── Pipfile
└── migrations/       # Flask-Migrate migration history
```