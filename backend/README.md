# Voice of a Girl — Django Backend

Programme management, beneficiary management, monitoring and impact measurement API.

**REACH → MANAGE → MONITOR → MEASURE → REPORT**

## Tech Stack

- Python / Django 5 / Django REST Framework
- JWT auth (SimpleJWT) with token blacklisting
- django-cors-headers, django-filter
- drf-spectacular (Swagger / OpenAPI at `/api/schema/` and `/api/docs/`)
- SQLite for local development (PostgreSQL-ready via `DATABASE_URL`)

## Quick Start

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # creates demo users + data
python manage.py runserver
```

Interactive API docs: <http://127.0.0.1:8000/api/docs/>

## Demo Credentials (after `seed_demo`)

| Role | Email | Password |
| --- | --- | --- |
| ADMIN | `admin@voiceofagirl.org` | `Admin@2026!` |
| ORGANISATION | `org@brightfuture.org` | `Org@2026!` |
| ORGANISATION (2nd) | `org@risinghope.org` | `Org@2026!` |

Participants do **not** have accounts; they complete surveys via secure public links.

## Demo Journey

1. ADMIN creates an organisation → 2. ORGANISATION logs in → 3. creates a programme
→ 4. participants register publicly → 5. participants enrolled → 6. baseline survey
created & published → 7. participants respond via public links → 8. challenges monitored
→ 9. endline survey completed → 10. analytics compare baseline/endline → 11. report exported.

## Apps

| App | Purpose |
| --- | --- |
| `accounts` | Custom two-role user model (ADMIN / ORGANISATION), JWT login/refresh/logout, admin user management |
| `organisations` | Organisation model + shared `OrganisationScopedModel` base |
| `participants` | Public registration, org-scoped participant management, verification |
| `programmes` | Programmes, objectives, KPIs, enrollments |
| `surveys` | Surveys, questions, assignments, responses, answers + public token links |
| `monitoring` | Programme challenges with categories and status workflow |
| `analytics` | Dashboards, KPI reports, baseline→endline→follow-up comparisons |
| `impact_projects` | Standalone paid impact-assessment projects for client orgs |
| `reports` | Structured report data + CSV/Excel export |

## API Overview

```
POST /api/auth/login/          POST /api/auth/refresh/      POST /api/auth/logout/
GET  /api/auth/me/             /api/auth/users/             (admin only)
POST /api/participants/register/     (public, no auth)
     /api/participants/        (search, filter, verify, claim)
     /api/programmes/          CRUD + /enroll/, /participants/, /kpis/
     /api/surveys/             CRUD + /publish/, /assign/, /completion_rate/
GET|POST /api/surveys/link/<token>/   (public survey form + submission)
     /api/monitoring/challenges/
     /api/analytics/programmes/<id>/    /summary/, /kpis/, /outcomes/
     /api/analytics/organisations/<id>/
     /api/reports/programmes/<id>/      /export/ (CSV)
     /api/impact-projects/
```

All data endpoints enforce organisation-level isolation at the queryset/permission level.
ADMIN sees everything; ORGANISATION users only ever see their own organisation's data.

## Testing

```bash
python manage.py test apps.accounts apps.participants apps.programmes apps.surveys apps.analytics
```

38 tests cover authentication/JWT flow, role permissions, organisation data isolation,
public registration, programme CRUD + enrollment, survey lifecycle, public survey
submission, analytics calculations and report exports.

## Environment

Copy `.env.example` → `.env` and set `DJANGO_SECRET_KEY` (and `DATABASE_URL` for
PostgreSQL in production). Never commit real credentials.
