# J4CMIS Frontend

React SPA (Vite + MUI) for the Justice for Children Management Information
System. Talks to the Django REST Framework API in `j4cmis_django_project`
via JWT.

## Decisions (see main project README for the full log)

- **React SPA + DRF API**, not Django templates -- chosen despite the
  added complexity relative to the "single on-prem box, no microservices"
  infra decision. JWT (access + refresh, rotation + blacklist) bridges the
  two.
- **Vite + MUI**, React Query for data fetching/caching, React Hook Form
  for forms.
- Deployed as a static build served from its own nginx `location /` on
  the same box as the Django API (`location /api/`) -- see
  `j4cmis_django_project/DEPLOYMENT.md` section 12.
- **No `@mui/icons-material` or `lucide-react`** -- both are 2,000+ file
  packages that repeatedly corrupted during this build's install process
  (truncated binaries, missing subdirectories). Icons are hand-authored
  SVG components in `src/icons/index.jsx`, matching the mockups' thin-line
  style. Add more there as new screens need them.

## Screens built so far

- **UC-01 Login** (`src/pages/LoginPage.jsx`) -- matches `ui/uc01.png`.
- **Dashboard** (`src/pages/DashboardPage.jsx`) -- matches
  `ui/appx_dashboard.png`, wired to live `/api/cases/` data (not mock
  data).
- **App shell** (`src/layout/AppShell.jsx`) -- full sidebar navigation
  transcribed from the dashboard mockup, covering all 27 use cases'
  entry points. Screens not yet built show a "coming in a later batch"
  stub rather than a dead link.

Everything else in the sidebar is a placeholder -- the API endpoints
behind them are live (see the Django project's `cases/api_urls.py`), but
the matching React screens are scheduled in later delivery batches.

## Local development

```bash
npm install
cp .env.example .env       # VITE_API_BASE_URL defaults to localhost:8000/api
npm run dev
```

Run the Django backend separately (`python manage.py runserver`) so the
API is reachable at the URL in `.env`.

## Production build

```bash
npm run build
```

Outputs to `dist/` -- see the Django project's `DEPLOYMENT.md` section 12
for the nginx config that serves this alongside the API on the same box.

## Login credentials note

The mockup shows an "Email Address" field; the backend currently
authenticates by Django username (see the Django project's README "Known
gap: username vs. email login"). Enter your username in that field for
now, or set usernames to match staff emails as a convention.

## Verified working

- `npm run build` completes cleanly (1,010 modules, ~582KB bundle).
- Login -> JWT issuance -> `/api/me/` -> Dashboard -> live case list, tested
  end-to-end against the real Django backend via Django's test client
  (including a CORS check simulating a browser request from the Vite dev
  origin).
