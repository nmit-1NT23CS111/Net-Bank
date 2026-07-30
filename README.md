# Net Bank

Net Bank is a simple online banking project using Django, MySQL, and React.

## Stack

- Backend: Django, Django REST Framework, Simple JWT
- Database: MySQL
- Frontend: React, TypeScript, Vite

## Backend

```powershell
cd backend
.\setup_mysql.ps1
.\venv\Scripts\python.exe manage.py runserver 8000
```

The setup script creates the MySQL database, writes `backend/.env`, installs Python dependencies, runs migrations, and seeds demo data.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The React app runs at `http://localhost:5173` and talks to `http://localhost:8000/api/v1`.

## Demo Login

- Customer: `demo@netbank.local` / `Demo@12345`
- Admin: `admin` / `Admin@12345`
