# Voice of a Girl

**B2B SaaS platform** for beneficiary management, programme monitoring, custom forms data collection, and outcome measurement for organisations empowering girls and young women.

## Features

- Role-based dashboards: Organisation Admin, Field Officer, Beneficiary, and Platform Admin
- Programme & participant management with enrollment and progress tracking
- Custom form builder and response collection
- Impact tracking and outcome measurement
- Monitoring, reporting, and verification workflows
- Challenges & opportunities portal for beneficiaries
- In-memory REST API (Express) for rapid prototyping, with a full Python/Django backend alongside

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS 4
- **Backend (prototype):** Node.js + Express with in-memory data (`server.ts`)
- **Backend (production path):** Django + PostgreSQL (`backend/`)
- **Libraries:** Recharts (charts), Motion (animation), Lucide (icons)

## Run Locally

**Prerequisites:** Node.js 20+

1. Install dependencies:

   ```bash
   npm install
   ```

2. (Optional) Create a local environment file:

   ```bash
   cp .env.example .env.local
   ```

3. Start the dev server:

   ```bash
   npm run dev
   ```

   The app will be available at **http://localhost:3000**.

## Scripts

| Command            | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `npm run dev`      | Start the dev server with hot reload on port 3000        |
| `npm run build`    | Build the frontend and bundle the Express server         |
| `npm run start`    | Run the production server (`dist/server.cjs`)            |
| `npm run lint`     | Type-check the project (`tsc --noEmit`)                  |
| `npm run clean`    | Remove build output                                      |

## Project Structure

```
backend/               Python (Django) backend
src/
  components/          React UI (landing, org, field, beneficiary, platform)
  context/             Auth context (mock in-browser auth)
  services/            API client for the Express REST endpoints
  types/               Shared TypeScript types
server.ts              Express server: REST API + in-memory data + Vite middleware
```
