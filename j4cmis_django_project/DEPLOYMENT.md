# J4CMIS — Deployment Guide

Target architecture per the Tayo conversation: single on-prem Linux box,
Django + Postgres + nginx, no microservices/Kubernetes. Government/IT
provides the box and a Postgres instance you connect to.

## 1. What you need from the government IT team before you start

- A Linux server (Ubuntu 22.04/24.04 recommended) you can SSH into with sudo.
- Either: (a) a Postgres instance/connection string, or (b) permission to
  install Postgres on the same box. Ask which — Tayo's point was you don't
  need bare metal specifically, just something you can connect to.
- A domain name or static internal IP for `DJANGO_ALLOWED_HOSTS`.
- Firewall rule: open port 443 (and 80 for redirect) inbound; DB port
  (5432) only needs to be reachable from the app itself.
- If mongo is ever introduced later, they provide that instance too — not
  applicable to this schema today (pure relational, Postgres only).

## 2. Server prep

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip \
    postgresql postgresql-contrib nginx git
```

If Postgres is on this box:

```bash
sudo -u postgres psql -c "CREATE DATABASE j4c_mis;"
sudo -u postgres psql -c "CREATE USER j4c_mis WITH PASSWORD 'change-me';"
sudo -u postgres psql -c "ALTER ROLE j4c_mis SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE j4c_mis TO j4c_mis;"
```

If Postgres is provided elsewhere, just get host/port/db/user/password from
IT — same env vars below either way.

## 3. Get the code onto the box

```bash
sudo mkdir -p /opt/j4cmis && sudo chown $USER:$USER /opt/j4cmis
cd /opt/j4cmis
git clone <your-repo-url> .          # or: unzip j4c_mis.zip -d /opt/j4cmis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Configure environment

```bash
cp .env.example .env
nano .env    # fill in DJANGO_SECRET_KEY, DB_*, DJANGO_ALLOWED_HOSTS, etc.
```

Generate a real secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Everything reads from `.env` via `python-dotenv` — load it before running
management commands:

```bash
export $(grep -v '^#' .env | xargs)
```//or use a process manager (below) that loads it for you.

## 5. Migrate, create roles, create admin user

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py bootstrap_roles
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

`bootstrap_roles` creates one auth Group per role in the ERD's USER.role
field (Administrator, Coordinator, Social Worker, Police/CID, DPP Officer,
Court Clerk, Facility Staff, Read-only Viewer) with sensible default
permissions. Assign staff to groups from `/admin/` → Authentication and
Authorization → Groups.

## 6. Run with gunicorn behind systemd

`/etc/systemd/system/j4cmis.service`:

```ini
[Unit]
Description=J4CMIS Django app
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/j4cmis
EnvironmentFile=/opt/j4cmis/.env
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
ExecStart=/opt/j4cmis/venv/bin/gunicorn config.wsgi:application \
    --workers 3 --bind unix:/opt/j4cmis/j4cmis.sock --timeout 60
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /opt/j4cmis
sudo systemctl daemon-reload
sudo systemctl enable --now j4cmis
sudo systemctl status j4cmis
```

Worker count: 3 is a safe default for the 30–100 user scale you gave Tayo.
Bump toward `(2 x CPU cores) + 1` if the box has more headroom.

## 7. nginx in front (same box, per Tayo's plan — "nginx will be on the linux box itself")

`/etc/nginx/sites-available/j4cmis`:

```nginx
server {
    listen 80;
    server_name j4cmis.example.ug;

    location /static/ {
        alias /opt/j4cmis/staticfiles/;
    }
    location /media/ {
        alias /opt/j4cmis/media/;
    }

    location / {
        proxy_pass http://unix:/opt/j4cmis/j4cmis.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/j4cmis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Add HTTPS with certbot once the domain is pointed at the box:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d j4cmis.example.ug
```

## 8. The single-point-of-failure tradeoff (flagged in the WhatsApp thread)

Everything — app, static files, and optionally Postgres — lives on one box.
Tayo's call was this is the right tradeoff at 30–100 users rather than
taking on microservices/Kubernetes complexity. To de-risk it without
re-architecting:

- **Back up Postgres nightly** (see below) and copy the dump off-box
  (another server, or cloud storage) — this is the part that actually
  matters if the box dies.
- **Back up `media/`** (uploaded documents — PF24 forms, SIR docs,
  agreements, evidence) the same way; it's not in the database.
- Keep `.env` and the systemd unit file backed up too — not sensitive
  enough to lose, but painful to reconstruct.
- If uptime requirements grow later, the next step is a warm standby box
  with Postgres streaming replication — still no microservices needed.

```bash
# /opt/j4cmis/backup.sh
#!/bin/bash
set -e
STAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U j4c_mis j4c_mis | gzip > /opt/backups/j4cmis_db_$STAMP.sql.gz
tar czf /opt/backups/j4cmis_media_$STAMP.tar.gz -C /opt/j4cmis media
find /opt/backups -mtime +30 -delete
```

Cron it nightly: `0 2 * * * /opt/j4cmis/backup.sh`

## 9. Deploying updates later

```bash
cd /opt/j4cmis
source venv/bin/activate
git pull                      # or re-upload changed files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart j4cmis
```

## 10. ORM performance (Tayo's flagged failure point)

CASE is the hub table — 10+ related tables hang off it. Watch for N+1
queries once real usage starts:

- Admin list views already use `select_related`/`autocomplete_fields`
  where it matters (see `cases/admin.py`).
- Any custom view iterating `case.arrest`, `case.classification`, etc. in
  a loop over many cases should use `select_related()`; iterating reverse
  FK sets (`case.court_proceedings.all()`, `case.documents.all()`, etc.)
  over many cases should use `prefetch_related()`.
- If a screen feels slow, first move is `django-debug-toolbar` in dev to
  see the query count before assuming it's a server-sizing problem.

## 11. Windows server variant

If IT hands you a Windows box instead of Linux, per Tayo: same process —
install Python + Postgres + nginx-for-windows (or IIS as reverse proxy
instead of nginx), same `git clone` + `pip install` + `.env` steps, run
gunicorn via a Windows service wrapper (e.g. NSSM) instead of systemd.

## 12. React frontend (added — see j4cmis_frontend/README.md decision log)

Architecture pivot from this project's original plan: a React SPA (Vite +
MUI) now sits in front of the API instead of Django templates, per
explicit instruction despite the added complexity this brings to the
single-box setup above. JWT (not session auth) bridges the SPA and API.

### Build and deploy

```bash
cd j4cmis_frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL to https://yourdomain/api
npm run build           # outputs to j4cmis_frontend/dist/
```

Copy `dist/` to the server, e.g. `/opt/j4cmis/frontend/dist`.

### nginx — two locations, one box (per the "separate nginx location, same box" decision)

```nginx
server {
    listen 80;
    server_name j4cmis.example.ug;

    location / {
        root /opt/j4cmis/frontend/dist;
        try_files $uri $uri/ /index.html;   # SPA routing fallback
    }

    location /api/ {
        proxy_pass http://unix:/opt/j4cmis/j4cmis.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://unix:/opt/j4cmis/j4cmis.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Additional env vars for `.env` (Django side)

```bash
CORS_ALLOWED_ORIGINS=https://j4cmis.example.ug
```

JWT access tokens expire after 30 minutes, refresh after 7 days, with
rotation and blacklisting on refresh (see `config/settings/base.py`
`SIMPLE_JWT`). No further nginx-level change needed for JWT — it's a
bearer token in the `Authorization` header, not a cookie, so no special
proxy handling is required.

### Known gap: username vs. email login

The mockup (UC-01) shows an "Email Address" field, but Django's built-in
`auth.User` authenticates by username, and DRF SimpleJWT's default
`TokenObtainPairView` expects `username`. This build has users log in with
their Django username (which can be set to their email address as a
matter of convention when creating accounts via `bootstrap_roles` /
`createsuperuser` / admin), but true email-as-username authentication
would need a custom authentication backend. Flagging rather than silently
deciding — tell me if this needs to be a real email-login flow before
go-live.
