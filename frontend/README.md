# Net Bank Frontend

React + Vite frontend for the Net Bank Django API.

## Requirements

- Node.js 20 or newer
- Backend API running at `http://localhost:8000`

## Run Locally

```powershell
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

To point the frontend at another API URL, create `.env.local`:

```text
VITE_API_URL=http://localhost:8000/api/v1
```

## Scripts

- `npm run dev` starts the Vite dev server.
- `npm run typecheck` runs TypeScript checks.
- `npm run build` type-checks and builds production assets.
- `npm run preview` serves the production build locally.

## App Surface

- Login and registration with JWT storage.
- Protected dashboard route.
- Account opening.
- Deposit, withdrawal, and transfer actions.
- Account and recent transaction views.
