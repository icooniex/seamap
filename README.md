# SEA-MaP Innovation & Investment Platform

SEA-MaP connects startups, investors, and corporates working on plastic circularity and waste management across Southeast Asia. It supports role-based onboarding, company profiles, matchmaking, challenges and problem statements, document management, and a verification-focused back office.

## Technology stack

| Area | Technology |
| --- | --- |
| Backend | Python 3.11, Django 4.2 |
| Database | PostgreSQL |
| Application server | Gunicorn |
| Static files | WhiteNoise |
| Object storage | Cloudflare R2 (S3-compatible) |
| Email and 2FA | Gmail SMTP |
| Deployment | Railway / Nixpacks |

## Prerequisites

- Python **3.11** (see `runtime.txt`)
- A running PostgreSQL instance; PostgreSQL 14+ is recommended
- `pip` and the standard `venv` module
- A Gmail account with an App Password only when sending real email
- A Cloudflare R2 account only when deploying persistent file uploads

## Local development setup

### 1. Clone the repository and create a virtual environment

```bash
git clone <repository-url>
cd seamap

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

### 2. Create the PostgreSQL database

For a locally installed PostgreSQL instance:

```bash
createdb seamap_db
```

Alternatively, create the database and user according to your team's database policy, then supply the connection values in `.env`.

### 3. Create `.env`

Create an `.env` file in the project root. It is excluded from Git.

```dotenv
# Django
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True

# Use either DATABASE_URL or the DB_* variables below.
# DATABASE_URL=postgresql://seamap_user:strong-password@localhost:5432/seamap_db
DB_NAME=seamap_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Optional: without this in DEBUG mode, emails are printed to the terminal.
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-gmail-app-password
```

When set, `DATABASE_URL` takes precedence over `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

### 4. Migrate, initialize media, and start the server

```bash
python manage.py migrate
python manage.py setup_media
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

Frequently used paths:

- `/` — home page
- `/signup/` and `/login/` — account registration and login
- `/dashboard/startups/` — dashboard and matchmaking
- `/backoffice/` — back office
- `/admin/` — Django admin; create a superuser first

### Useful management commands

```bash
# Create a Django administrator
python manage.py createsuperuser

# Load a compact demo data set
python manage.py load_sample_data

# Load the complete sample data set (six companies).
# --force recreates or updates sample records.
python manage.py load_full_sample_data

# Test OTP email delivery
python manage.py test_2fa_email --email recipient@example.com

# Check production-oriented Django settings
python manage.py check --deploy
```

Do not run `load_full_sample_data --force` against a production database containing real data without first assessing its impact.

## Email configuration

The application uses Gmail SMTP over TLS at `smtp.gmail.com:587` for OTP and notification emails. With `DEBUG=True` and no `EMAIL_HOST_USER`, Django uses the console email backend and prints emails to the terminal instead.

For Gmail, enable 2-Step Verification and generate an **App Password**. Set it only through `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`; never commit it to the repository. See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed setup steps.

## File uploads and Cloudflare R2

Local development stores uploads in `media/`. `python manage.py setup_media` creates the expected directories and default files.

When `RAILWAY_ENVIRONMENT` is present, Cloudflare R2 is enabled automatically unless `USE_CLOUDFLARE_R2=false` is set. Configure the following Railway environment variables:

```dotenv
USE_CLOUDFLARE_R2=true
CLOUDFLARE_R2_ACCESS_KEY_ID=<r2-access-key-id>
CLOUDFLARE_R2_SECRET_ACCESS_KEY=<r2-secret-access-key>
CLOUDFLARE_R2_BUCKET_NAME=seamap-media
CLOUDFLARE_R2_ENDPOINT_URL=https://<cloudflare-account-id>.r2.cloudflarestorage.com
# Optional but recommended for serving media
CLOUDFLARE_R2_CUSTOM_DOMAIN=media.example.com
```

Allowed uploads are PDF, Word, PowerPoint, JPG/JPEG, PNG, and GIF files. The maximum request and uploaded-file size is 25 MB. For bucket creation, API tokens, and custom-domain configuration, see [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md).

## Deploying to Railway

1. Create a Railway project and connect this Git repository.
2. Add a PostgreSQL service, then link its `DATABASE_URL` to the web service.
3. Add at least these production variables:

   ```dotenv
   SECRET_KEY=<long-random-secret>
   DEBUG=False
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

4. Add the R2 variables above if uploaded files must persist.
5. Configure a Railway public domain. Confirm it is included in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` through `RAILWAY_PUBLIC_DOMAIN` / `RAILWAY_STATIC_URL`, or update `seamap/settings.py` for a custom domain.
6. Push to the branch Railway tracks, or deploy from the Railway dashboard.

`railway.json` selects Nixpacks and defines the deployment command. `Procfile` is available for platforms that use Procfiles. Deployment runs migrations, prepares static files, and starts Gunicorn on the port provided through `$PORT`.

> **Important:** `railway.json` currently runs `python manage.py load_full_sample_data --force` on every deployment. This is appropriate only for staging or demo environments. Remove that command from `startCommand` before deploying a real production database; otherwise every deployment can create or alter sample records.

### Post-deployment checks

```bash
python manage.py check --deploy
python manage.py test_2fa_email --email recipient@example.com
```

Also verify account registration, login and 2FA, file uploads, and access to media through the R2 custom domain.

## Dependencies and third-party services

| Dependency or service | Purpose |
| --- | --- |
| [Django](https://www.djangoproject.com/) 4.2.23 | Web framework, authentication, ORM, migrations, admin, and template rendering |
| [psycopg](https://www.psycopg.org/psycopg3/) | PostgreSQL driver used by Django |
| [Gunicorn](https://gunicorn.org/) | WSGI application server used in production |
| [WhiteNoise](https://whitenoise.readthedocs.io/) | Serves and compresses static assets in production |
| [Pillow](https://python-pillow.org/) | Image-field and image-file processing |
| [django-storages](https://django-storages.readthedocs.io/) and [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) | S3-compatible storage backend for Cloudflare R2 |
| [dj-database-url](https://github.com/jazzband/dj-database-url) | Parses `DATABASE_URL` into Django database settings |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Loads local environment variables from `.env` |
| [python-decouple](https://github.com/HBNetwork/python-decouple) | A configuration dependency locked in `requirements.txt`; it is not currently imported by the application source |
| [Cloudflare R2](https://www.cloudflare.com/developer-platform/r2/) | Persistent object storage for profile photos, company logos, and documents on Railway |
| [Gmail SMTP](https://support.google.com/mail/answer/185833) | Delivers OTP and notification emails using a Gmail App Password |
| [Railway](https://railway.com/) | Hosting, runtime environment, and managed PostgreSQL integration |

All pinned Python package versions are listed in [requirements.txt](requirements.txt), helping development and production environments stay consistent.

## Project structure

```text
seamap/                 # Django settings, URL routes, WSGI/ASGI, and R2 backend
member/                 # Membership, onboarding, matchmaking, documents, management commands
backoffice/             # Administration and verification workflows
templates/              # Django templates organized by feature
static/                 # CSS, JavaScript, images, and public documents
requirements.txt        # Pinned Python dependencies
railway.json            # Railway build and deployment configuration
Procfile                # Process definition for Procfile-based deployments
```

## Security and maintenance

- Keep `SECRET_KEY`, database passwords, Gmail App Passwords, and R2 credentials in environment variables only.
- Always set `DEBUG=False` in production.
- Use HTTPS and review `CSRF_TRUSTED_ORIGINS` whenever adding a custom domain.
- Back up PostgreSQL and R2 on a schedule appropriate to the service.
- Before upgrading dependencies, test migrations, uploads, and the 2FA flow in staging before production deployment.
