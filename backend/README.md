# Voice of a Girl — B2B SaaS Platform

**Voice of a Girl** is a B2B SaaS platform for beneficiary management, programme monitoring, data collection, and outcome measurement.

Initial target market: Organisations empowering girls and young women (with an extensible architecture supporting diverse beneficiary demographics and programme archetypes).

---

## Core Value Proposition

### **REACH → MANAGE → COLLECT → MONITOR → RESPOND → MEASURE → REPORT**

- **For a New Programme**:
  `Create Programme` → `Find Beneficiaries` → `Select Participants` → `Collect Data` → `Monitor` → `Respond` → `Measure Outcomes` → `Report`

- **For an Existing Programme**:
  `Register Programme` → `Add Participants` → `Collect Data` → `Monitor Progress` → `Identify Challenges` → `Measure Results` → `Report`

---

## Architecture & Technology Stack

### Backend Architecture (Django Modular Structure)
- **Framework**: Django 5 + Django REST Framework (DRF)
- **Database**: PostgreSQL / SQLite (Django ORM)
- **Authentication**: JWT (JSON Web Tokens) with Role-Based Access Control (RBAC)
- **Modules**:
  - `apps/accounts`: Custom User Model with 4 distinct roles (`BENEFICIARY`, `ORGANISATION_ADMIN`, `FIELD_OFFICER`, `PLATFORM_ADMIN`).
  - `apps/organisations`: Organisation entity management and multi-tenant scoping.
  - `apps/beneficiaries`: Secure beneficiary profile, demographics, education, skills, and interests.
  - `apps/programmes`: New and ongoing programme models with criteria rules.
  - `apps/opportunities`: Scholarships, internships, jobs, seed grants, and training programs.
  - `apps/applications`: Application submission, deduplication, and selection pipeline.
  - `apps/participation`: Participant lifecycle tracking (`REGISTERED` → `SELECTED` → `ACTIVE` → `COMPLETED` → `DROPPED_OUT`).
  - `apps/forms`: Google Forms-style dynamic form engine supporting:
    - 4 Lifecycle Types: `BASELINE`, `MONITORING`, `ENDLINE`, `FOLLOW_UP`, and `CUSTOM`
    - 10 Question Types: Short text, Long text, Number, Multiple choice, Checkbox, Dropdown, Yes/No, Rating scale (1-5/1-10), Date, File upload.
  - `apps/challenges`: Early warning challenge tracking system with severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), status lifecycle, and response assignment workflow.
  - `apps/impact`: KPI management (`INPUT`, `ACTIVITY`, `OUTPUT`, `OUTCOME`, `IMPACT`) and longitudinal Before → After → Change tracking.
  - `apps/monitoring`: Real-time attendance, satisfaction, and dropout risk analytics.
  - `apps/verification`: Field officer task assignments, home visits, and GPS confirmation.
  - `apps/notifications`: Multi-channel notification pipeline (In-app, Email ready, SMS/WhatsApp ready).
  - `services/matching_engine.py`: Transparent rule-based match score engine comparing location, age, education, skills, and goals.

### Frontend Architecture
- **Framework**: React 19 + TypeScript + Vite
- **UI & Layout**: Tailwind CSS v4 + Motion animations + Lucide icons
- **Data Visualizations**: Recharts (Funnel, Bar, Line, and Donut charts)
- **Exporting**: Instant print/PDF reporting and CSV/Excel dataset exports

---

## RESTful API Endpoints Specification

### Authentication
- `POST /api/auth/register/` — Register new user (Beneficiary, Org Admin, or Field Officer)
- `POST /api/auth/login/` — Authenticate and receive JWT tokens + role claims
- `POST /api/auth/refresh/` — Refresh access token
- `GET /api/auth/me/` — Retrieve current authenticated user profile & role

### Programmes & Management
- `GET /api/programmes/` — List organization's programmes
- `POST /api/programmes/` — Create new or register existing programme
- `GET /api/programmes/{id}/` — Programme details and KPIs
- `GET /api/programmes/{id}/participants/` — List enrolled beneficiaries and match metrics
- `POST /api/programmes/{id}/participants/` — Enroll beneficiary into programme
- `PATCH /api/participation/{id}/` — Update participation status (Active, Completed, Dropped Out)

### Custom Forms Engine
- `GET /api/programmes/{id}/forms/` — List programme forms (Baseline, Monitoring, Endline, Follow-up)
- `POST /api/programmes/{id}/forms/` — Create custom form with Google Forms-style questions
- `GET /api/forms/{id}/` — Fetch form structure and questions
- `POST /api/forms/{id}/publish/` — Publish form to enrolled participants
- `POST /api/forms/{id}/submit/` — Submit responses to a form
- `GET /api/forms/{id}/responses/` — View aggregate & individual answers

### Challenge Tracking & Response Workflow
- `GET /api/programmes/{id}/challenges/` — Retrieve challenges for programme
- `POST /api/programmes/{id}/challenges/` — Report a challenge (by participant or field officer)
- `PATCH /api/challenges/{id}/` — Update challenge details or notes
- `POST /api/challenges/{id}/assign/` — Assign field officer / response team member
- `POST /api/challenges/{id}/resolve/` — Mark resolved with resolution notes & audit history

### Analytics & Outcome Measurement
- `GET /api/programmes/{id}/analytics/` — Core metrics (Funnel, Attendance, Dropouts, KPIs)
- `GET /api/programmes/{id}/challenge-analytics/` — Aggregated recurring issues and severity breakdown
- `GET /api/programmes/{id}/outcomes/` — Before → After → Change comparison (Baseline vs. Endline vs. Follow-up)

---

## Getting Started

### Backend Setup (Python / Django)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### Frontend Setup & Dev Server
```bash
npm install
npm run dev
```
Open `http://localhost:3000` to interact with the full-stack platform.
