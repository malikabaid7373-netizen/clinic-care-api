# ClinicCare API

Production-style portfolio backend for the ClinicCare appointment platform.

## Stack

- Django 5.2
- Django REST Framework
- Simple JWT with refresh-token blacklisting
- SQLite for local portfolio development

## Features

- Patient registration, login, refresh, logout, and current-user API
- Password validation and unique email checks
- Public read-only doctor directory
- Weekly doctor schedules and live free-slot generation
- Authenticated appointment creation
- Appointment ownership: patients only see and cancel their own bookings
- Duplicate-slot protection at serializer and database level
- Admin appointment confirmation/completion/cancellation actions
- API tests for authentication, slots, ownership, and booking

## Quick start on Windows

```powershell
cd "C:\Users\Bismi\Desktop\Personal Projects\clinic-care-api"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\setup.ps1
.\run.ps1
```

Or manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_doctors
python manage.py seed_demo
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`

Admin: `http://127.0.0.1:8000/admin/`

## Create an admin

```powershell
python manage.py createsuperuser
```

## Local demo login

After running `python manage.py seed_demo`, use:

- Email: `demo@cliniccare.local`
- Password: `ClinicDemo@123`

This account is for local portfolio demonstrations only. Remove it or change the password before any public deployment.

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

## Tests

```powershell
python manage.py check
python manage.py test
```

## Local database and backup

Local data is stored permanently in `db.sqlite3`. It survives server stops and laptop restarts.

Create a backup while the server is stopped:

```powershell
New-Item -ItemType Directory -Force .\backups
Copy-Item .\db.sqlite3 ".\backups\db-$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').sqlite3"
```

The included database contains portfolio demo data. Do not commit real patient data to GitHub. For a real deployment, move to PostgreSQL and set environment variables from `.env.example` through the hosting platform.
