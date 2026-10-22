# Healthcare Backend (Django + DRF + PostgreSQL)

A REST API for a healthcare application: users register and log in with JWT, then manage **patients**, **doctors**, and the **assignments** between them. All data is stored in PostgreSQL.

Built for the WhatBytes Full-stack Developer Internship assignment.

## Tech stack

| Concern        | Choice                                    |
| -------------- | ----------------------------------------- |
| Framework      | Django 5.2, Django REST Framework 3.16    |
| Auth           | JWT via `djangorestframework-simplejwt`   |
| Database       | PostgreSQL 16 (via `psycopg` 3)           |
| Config         | Environment variables (`.env` + `python-dotenv`) |
| Python         | 3.10+ (developed on 3.12)                 |

## Project structure

```
.
├── config/                 # Project settings, root URLs, JSON exception handler
├── accounts/               # Custom User (email login), register + login endpoints
├── patients/               # Patient model + CRUD (scoped to the creating user)
├── doctors/                # Doctor model + CRUD (shared directory, creator-only writes)
├── mappings/               # Patient <-> Doctor assignments
├── docs/
│   └── healthcare-api.postman_collection.json
├── docker-compose.yml      # Local PostgreSQL
├── requirements.txt
└── .env.example            # Copy to .env
```

Each app follows the same layout: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `tests.py`.

## Getting started

### 1. Clone and install

```bash
git clone <repo-url>
cd Assignment-WhatBytes
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Then edit `.env`. At minimum set a real `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"   # use as DJANGO_SECRET_KEY
```

| Variable               | Required | Default               | Description                         |
| ---------------------- | -------- | --------------------- | ----------------------------------- |
| `DJANGO_SECRET_KEY`    | yes      | –                     | Django secret key                   |
| `DJANGO_DEBUG`         | no       | `False`               | `True` for local development        |
| `DJANGO_ALLOWED_HOSTS` | no       | `localhost,127.0.0.1` | Comma-separated hostnames           |
| `POSTGRES_DB`          | yes      | –                     | Database name                       |
| `POSTGRES_USER`        | yes      | –                     | Database user                       |
| `POSTGRES_PASSWORD`    | yes      | –                     | Database password                   |
| `POSTGRES_HOST`        | no       | `localhost`           | Database host                       |
| `POSTGRES_PORT`        | no       | `5432`                | Database port                       |
| `JWT_ACCESS_MINUTES`   | no       | `60`                  | Access token lifetime (minutes)     |
| `JWT_REFRESH_DAYS`     | no       | `1`                   | Refresh token lifetime (days)       |

The app refuses to start if a required variable is missing.

### 3. Start PostgreSQL

With Docker (uses the credentials from `.env`):

```bash
docker compose up -d
```

Or use an existing PostgreSQL server and create a database/user that match your `.env`.

### 4. Migrate and run

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

The API is now at `http://localhost:8000/api/`, and the Django admin is at `http://localhost:8000/admin/`.

## Authentication

1. `POST /api/auth/register/` to create an account.
2. `POST /api/auth/login/` with email + password to get an `access` and a `refresh` token.
3. Send the access token on every other request:

```
Authorization: Bearer <access token>
```

When the access token expires, exchange the refresh token at `POST /api/auth/token/refresh/`.

All patient, doctor, and mapping endpoints require authentication. Requests without a valid token get `401`.

## API reference

Base URL: `http://localhost:8000`. List endpoints are paginated (20 per page, `?page=N`) and return `{count, next, previous, results}`.

### Auth

| Method | Endpoint                   | Auth | Description                    |
| ------ | -------------------------- | ---- | ------------------------------ |
| POST   | `/api/auth/register/`      | No   | Register with name, email, password |
| POST   | `/api/auth/login/`         | No   | Get JWT access + refresh tokens |
| POST   | `/api/auth/token/refresh/` | No   | Get a new access token          |

**Register**

```http
POST /api/auth/register/
{ "name": "Saksham Jain", "email": "saksham@example.com", "password": "Str0ng-pass!" }
```
```json
201 Created
{ "id": 1, "name": "Saksham Jain", "email": "saksham@example.com" }
```

Emails are case-insensitive and unique. Passwords go through Django's password validators (minimum length, not too common, not all numeric, not too similar to name/email).

**Login**

```http
POST /api/auth/login/
{ "email": "saksham@example.com", "password": "Str0ng-pass!" }
```
```json
200 OK
{ "refresh": "eyJhbGciOi...", "access": "eyJhbGciOi..." }
```

### Patients

| Method | Endpoint              | Description                                    |
| ------ | --------------------- | ---------------------------------------------- |
| POST   | `/api/patients/`      | Add a patient                                  |
| GET    | `/api/patients/`      | List patients **created by the current user**  |
| GET    | `/api/patients/<id>/` | Patient details                                |
| PUT    | `/api/patients/<id>/` | Update a patient (full update)                 |
| DELETE | `/api/patients/<id>/` | Delete a patient                               |

```http
POST /api/patients/
{
  "name": "Ravi Kumar",
  "date_of_birth": "1990-05-14",
  "gender": "male",
  "phone": "+919876543210",
  "email": "ravi@example.com",
  "address": "Ghaziabad, UP",
  "medical_history": "Mild asthma"
}
```
```json
201 Created
{
  "id": 1, "name": "Ravi Kumar", "date_of_birth": "1990-05-14", "gender": "male",
  "phone": "+919876543210", "email": "ravi@example.com", "address": "Ghaziabad, UP",
  "medical_history": "Mild asthma", "created_by": "saksham@example.com",
  "created_at": "2026-10-22T16:11:28.524831Z", "updated_at": "2026-10-22T16:11:28.524834Z"
}
```

- Required fields: `name`, `date_of_birth` (YYYY-MM-DD, not in the future), `gender` (`male` | `female` | `other`), and `phone` (7–15 digits, optional leading `+`).
- Optional fields: `email`, `address`, `medical_history`.
- Patients are private to their creator. Another user's patient id returns `404`, so the API doesn't reveal that the record exists.

### Doctors

| Method | Endpoint             | Description                          |
| ------ | -------------------- | ------------------------------------ |
| POST   | `/api/doctors/`      | Add a doctor                         |
| GET    | `/api/doctors/`      | List **all** doctors                 |
| GET    | `/api/doctors/<id>/` | Doctor details                       |
| PUT    | `/api/doctors/<id>/` | Update a doctor (creator only)       |
| DELETE | `/api/doctors/<id>/` | Delete a doctor (creator only)       |

```http
POST /api/doctors/
{
  "name": "Meera Shah",
  "specialization": "Cardiology",
  "email": "meera.shah@clinic.com",
  "phone": "9876500000",
  "experience_years": 12
}
```

- Required fields: `name`, `specialization`, `email` (unique across doctors), and `phone`.
- Optional field: `experience_years` (0–70, default 0).
- Doctors form a shared directory: every authenticated user can list them and assign them to their own patients. Only the user who created a doctor can update or delete it; anyone else gets `403`.

### Patient–doctor mappings

| Method | Endpoint                       | Description                                       |
| ------ | ------------------------------ | ------------------------------------------------- |
| POST   | `/api/mappings/`               | Assign a doctor to a patient                      |
| GET    | `/api/mappings/`               | List all mappings for the current user's patients |
| GET    | `/api/mappings/<patient_id>/`  | List the doctors assigned to a patient            |
| DELETE | `/api/mappings/<mapping_id>/`  | Remove a doctor from a patient                    |

> **Note:** As in the assignment spec, `/api/mappings/<id>/` takes a **patient id** for `GET` and a **mapping id** for `DELETE`.

```http
POST /api/mappings/
{ "patient": 1, "doctor": 1, "notes": "Routine cardiac check-up" }
```
```json
201 Created
{
  "id": 1, "patient": 1, "patient_name": "Ravi Kumar", "doctor": 1,
  "doctor_name": "Meera Shah", "doctor_specialization": "Cardiology",
  "notes": "Routine cardiac check-up", "created_at": "2026-10-22T16:11:28.601468Z"
}
```

`GET /api/mappings/1/` returns a list of doctor objects (same shape as `/api/doctors/<id>/`).

- You can only assign doctors to **your own** patients. Another user's patient id is rejected with `400`.
- Assigning the same doctor to the same patient twice returns `400`. A database unique constraint also enforces this.
- Deleting a patient or doctor also removes their mappings.

## Error handling

Errors are always JSON, with an HTTP status that matches the problem:

| Status | When                                   | Example body                                                   |
| ------ | -------------------------------------- | -------------------------------------------------------------- |
| 400    | Validation failed / malformed JSON     | `{"phone": ["Enter a valid phone number (7-15 digits, optional leading +)."]}` |
| 401    | Missing, invalid, or expired token; wrong login | `{"detail": "Authentication credentials were not provided."}` |
| 403    | Modifying a doctor you didn't create   | `{"detail": "Only the user who created this record can modify or delete it."}` |
| 404    | Record doesn't exist or isn't yours    | `{"detail": "No Patient matches the given query."}`            |
| 405    | Unsupported method (e.g. `PATCH`)      | `{"detail": "Method \"PATCH\" not allowed."}`                  |
| 409    | Database conflict (e.g. a race on a unique field) | `{"detail": "This record conflicts with an existing one."}` |
| 500    | Unexpected error (logged server-side)  | `{"detail": "Internal server error."}`                         |

Validation errors are keyed by field name, so a client can show each error next to its form input.

## Testing

### Automated tests

The suite has 17 tests covering auth, CRUD, validation, and cross-user access rules. It runs against PostgreSQL, so start the database first:

```bash
python manage.py test
```

### Postman

1. Import `docs/healthcare-api.postman_collection.json` into Postman.
2. Run the folders in order: **Auth → Patients → Doctors → Mappings → Cleanup**.

**Login** saves the access token to the collection variables, and each **Create** request saves the new id, so later requests work without copy-pasting. If your server isn't on `http://localhost:8000`, change the `baseUrl` collection variable.

## Design decisions

- **Custom user model with email login.** The spec registers users with name, email, and password, with no username. The custom model is defined before the first migration, as Django recommends.
- **Patients are per-user and doctors are shared.** The spec says "retrieve all patients *created by the authenticated user*" but "retrieve *all* doctors", and the API follows that wording.
- **Ownership is enforced in the queryset.** Patients and mappings are filtered by the current user, so another user's record behaves as if it doesn't exist (404).
- **Only `PUT` updates, no `PATCH`.** The spec lists only `PUT`, which does a full update.
- **Secrets only in the environment.** `.env` is git-ignored and `.env.example` documents every variable.
