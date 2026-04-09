# HostelOrbit - Hostel Management System

Flask hostel management app with modular blueprints, role-based auth, modern dashboard UI, and SQLite DB (PostgreSQL-ready via `DATABASE_URL`).

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Modules
- Auth and RBAC (Student/Admin)
- Room and inventory management
- Finance invoices, penalties, and mock UPI
- Mess menu, voting, and waste tracking
- Complaints service desk
- Out-pass, QR simulation, SOS
- Marketplace and lost & found
- Analytics with Chart.js
