# Lenscape Backend — Run & Deploy

## Local development
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python app.py                # Flask dev server with auto-reload + debug
```
Runs on `http://localhost:5000`. Keep `FLASK_ENV=development` in `.env`.

> Note: Gunicorn only runs on Linux/macOS. On Windows for a production-like
> local test use Waitress: `python run_production.py`.

## Production (Linux host — Render / Railway / Fly / VPS)
```bash
pip install -r requirements.txt
gunicorn -c gunicorn_config.py wsgi:app
```
Or rely on the `Procfile` (Render/Railway/Heroku auto-detect it).

### Required production env vars
Set these in your host's dashboard (do NOT commit secrets):

| Var | Notes |
|---|---|
| `FLASK_ENV` | `production` |
| `CORS_ORIGINS` | Your frontend URL, e.g. `https://lenscape.vercel.app` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Full service-account JSON string (preferred on cloud) |
| `ADMIN_SECRET_KEY` | Master key for admin registration |
| `ADMIN_JWT_SECRET` / `USER_JWT_SECRET` / `OTP_SECRET` | Strong random strings |
| `SMTP2GO_API_KEY` / `SENDER_EMAIL` | OTP and moderation email delivery |
| `CLOUDINARY_*` | Cloudinary creds |

`PORT` is provided automatically by most hosts; `gunicorn_config.py` reads it.

### Tuning (optional env)
- `WEB_CONCURRENCY` — worker count (default: 2×CPU + 1)
- `GUNICORN_THREADS` — threads per worker (default: 4)
- `GUNICORN_TIMEOUT` — request timeout seconds (default: 60)

## Firestore data migration

Use `scripts/migrate_firestore.py` to copy the Lenscape Firestore collections
from an old Firebase project into the current project. It preserves document IDs
and is dry-run by default.

Before running it:
- Create/enable the default Firestore database in the destination Firebase project.
- Keep service-account JSON files local or pass JSON through environment vars.
- Do not use the frontend `VITE_FIREBASE_*` web config for migration; it is not an admin credential.

Default collections copied:
`users`, `artworks`, `categories`, `banned_users`, `admins`

Dry-run:
```bash
SOURCE_FIREBASE_SERVICE_ACCOUNT=/absolute/path/old-service-account.json \
DEST_FIREBASE_SERVICE_ACCOUNT=/absolute/path/new-service-account.json \
python scripts/migrate_firestore.py
```

Execute:
```bash
SOURCE_FIREBASE_SERVICE_ACCOUNT=/absolute/path/old-service-account.json \
DEST_FIREBASE_SERVICE_ACCOUNT=/absolute/path/new-service-account.json \
python scripts/migrate_firestore.py --execute
```

To pass credentials as JSON strings instead of file paths, use
`SOURCE_FIREBASE_SERVICE_ACCOUNT_JSON` and `DEST_FIREBASE_SERVICE_ACCOUNT_JSON`.
Set `FIRESTORE_MIGRATION_COLLECTIONS=users,artworks` to migrate a subset.
