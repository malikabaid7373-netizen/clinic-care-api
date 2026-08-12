# ClinicCare API

Production-style Django REST backend for the ClinicCare bilingual appointment booking portfolio application.

## Live API

`https://clinic-care-api-production.up.railway.app/api/`

## Stack

- Django 5.2
- Django REST Framework
- Simple JWT with refresh-token rotation and blacklisting
- PostgreSQL on Railway in production
- SQLite for local development
- Gunicorn + WhiteNoise for production hosting

## Features

- Patient registration, login, token refresh, logout, and current-user API
- Password validation and duplicate-email protection
- Public read-only doctor directory
- Weekly doctor schedules and live free-slot generation
- Authenticated appointment creation
- Patient ownership: users can only read/cancel their own appointments
- Server-owned patient name, email, fee, and appointment status
- Duplicate active-slot protection at validation and database levels
- Future-only cancellation protection
- Admin appointment confirmation/completion management
- Dashboard appointment summary endpoint
- Production PostgreSQL support through `DATABASE_URL`

## Local setup

```powershell
cd "C:\Users\Bismi\Desktop\Personal Projects\clinic-care-api"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_doctors
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`

Admin: `http://127.0.0.1:8000/admin/`

## Important endpoints

- `GET /api/health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/doctors/`
- `GET /api/doctors/{id}/available-slots/?date=YYYY-MM-DD`
- `GET|POST /api/appointments/`
- `GET /api/appointments/summary/`
- `POST /api/appointments/{id}/cancel/`

## Checks

```powershell
python manage.py check
python manage.py test
```

## Production variables

Use the hosting platform's secret manager. Never commit the real `.env` file.

```env
DJANGO_SECRET_KEY=replace-with-a-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-api-domain
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-api-domain
DJANGO_TIME_ZONE=Asia/Riyadh
DATABASE_URL=postgresql://...
```
