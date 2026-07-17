# J4C MIS - Justice for Children Management Information System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js: 20+](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Status: Development](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/abilajoshuaalan/J4C-MIS)

A comprehensive Django + React full-stack Management Information System for tracking and managing justice cases for children in Uganda. The system handles case management, child welfare tracking, legal proceedings, and rehabilitation processes.

---

## 🎯 Quick Start

Get the system running in **5 minutes**:

### Prerequisites
- Python 3.9+ ([install](https://www.python.org/downloads/))
- Node.js 20+ ([install](https://nodejs.org/))
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/abilajoshuaalan/J4C-MIS.git
cd J4C-MIS
```

### 2. Set Up Backend (Terminal 1)
```bash
cd j4cmis_django_project
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_roles
python manage.py createsuperuser  # Create admin user
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver
```

Backend runs on: **http://127.0.0.1:8000/**

### 3. Set Up Frontend (Terminal 2)
```bash
cd j4cmis_frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:5173/**

### 4. Access the System
- **Frontend (UI):** http://localhost:5173/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Documentation:** http://127.0.0.1:8000/api/

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (React)                      │
│                  http://localhost:5173                      │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────────────┐
         │ Material-UI Components        │
         │ React Router Navigation       │
         │ React Query Data Fetching     │
         │ Axios HTTP Client             │
         └───────────┬───────────────────┘
                     │ (CORS Enabled)
         ┌───────────▼───────────────────┐
         │   Django REST Framework       │
         │   http://127.0.0.1:8000       │
         │   JWT Authentication          │
         │   Role-Based Access Control   │
         │   34 Django Models            │
         └───────────┬───────────────────┘
                     │
         ┌───────────▼───────────────────┐
         │   SQLite Database             │
         │   (Local Development)         │
         │   PostgreSQL (Production)     │
         └───────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 19.2.7 | UI Components & Pages |
| **Frontend** | Vite | 8.1.1 | Build Bundler |
| **Frontend** | Material-UI | 6.1.0 | Component Library |
| **Frontend** | React Router | 7.18.1 | Navigation |
| **Backend** | Django | 4.2.30 | Web Framework |
| **Backend** | DRF | 3.16.1 | REST API |
| **Backend** | Django SimpleJWT | 5.5.1 | Authentication |
| **Database** | SQLite | - | Local Development |
| **Database** | PostgreSQL | - | Production |

---

## 📁 Project Structure

```
J4C-MIS/
├── j4cmis_django_project/          # Backend (Django)
│   ├── cases/                       # Main application
│   │   ├── models.py               # 39 data models
│   │   ├── views.py                # API views
│   │   ├── serializers.py          # DRF serializers
│   │   └── admin.py                # Admin interface
│   ├── config/                      # Django settings
│   │   ├── settings/
│   │   │   ├── base.py             # Base configuration
│   │   │   ├── dev.py              # Development settings
│   │   │   └── prod.py             # Production settings
│   │   ├── urls.py                 # URL routing
│   │   └── wsgi.py                 # WSGI config
│   ├── manage.py                   # Django CLI
│   ├── requirements.txt             # Python dependencies
│   └── README.md                   # Backend documentation
│
├── j4cmis_frontend/                 # Frontend (React)
│   ├── src/
│   │   ├── components/             # Reusable React components
│   │   ├── pages/                  # Page components
│   │   ├── services/               # API service calls
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── context/                # React Context providers
│   │   └── App.jsx                 # Main app component
│   ├── public/                      # Static assets
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite configuration
│   └── README.md                   # Frontend documentation
│
├── README.md                        # This file
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
└── DEPLOYMENT_SUMMARY.md            # Deployment notes
```

---

## 🔐 Authentication & Authorization

### Three User Roles

1. **System Administrator** — Full access to all features and data
2. **National Coordinator** — Access to national-level data and reports
3. **Regional Coordinator** — Access to assigned region's data only

### JWT Authentication

The system uses **JSON Web Tokens (JWT)** for API authentication:

```bash
# Obtain token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/cases/
```

---

## 🗂️ Key Features

### Case Management
- ✅ Case creation with auto-generated case numbers
- ✅ Case status tracking with history audit trail
- ✅ Multiple case types (Child Victim, Juvenile Accused, Vulnerable)
- ✅ Regional scoping for coordinators

### Child Welfare
- ✅ Child profile management
- ✅ Guardian/parent tracking
- ✅ Age determination
- ✅ Rehabilitation and resettlement plans

### Legal Proceedings
- ✅ Court proceeding tracking
- ✅ DPP/RSA routing
- ✅ Legal representation management
- ✅ Arrest and classification records

### Monitoring & Reporting
- ✅ Progress tracking for rehabilitation
- ✅ Facility inspection records
- ✅ Victim impact assessments
- ✅ Diversion plan monitoring

### Data Models (39 Total)
Case, Child, Guardian, Arrest, Classification, SocialInquiryReport, VictimImpactAssessment, DiversionPlan, ReferralInstitution, ChildFriendlySpace, DPPRouting, CourtProceeding, RemandPlacement, Document, AgeDetermination, ActivityChain, Rehabilitation, Resettlement, CommunityService, LegalRepresentation, Training, BreastfeedingMotherAccompanyingChild, SuspectParade, FacilityInspection, UserProfile, CaseStatusHistory, and more...

---

## 🚀 Deployment

### Local Development
The quickest setup uses SQLite for the database:

```bash
# Backend uses SQLite automatically when USE_SQLITE=1 (default)
DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver
```

### Production Deployment
For production deployment with PostgreSQL, see [`j4cmis_django_project/DEPLOYMENT.md`](./j4cmis_django_project/DEPLOYMENT.md)

**Key requirements:**
- PostgreSQL database
- Environment variables for secrets
- Gunicorn for WSGI serving
- Nginx for reverse proxy
- HTTPS/TLS certificate

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [Backend README](./j4cmis_django_project/README.md) | Django setup & architecture |
| [Frontend README](./j4cmis_frontend/README.md) | React setup & components |
| [Deployment Guide](./j4cmis_django_project/DEPLOYMENT.md) | Production deployment steps |
| [SRS Document](./J4C-MIS-SRS-v1.4.docx) | System Requirements Specification |
| [Architecture Diagram](./J4C-MIS-architecture-diagram.png) | System architecture overview |

---

## 🧪 Testing

### Run Backend Tests
```bash
cd j4cmis_django_project
source venv/bin/activate
python manage.py test cases
```

### Run Frontend Linting
```bash
cd j4cmis_frontend
npm run lint
```

---

## 🔧 Development Workflow

### Backend Changes
```bash
cd j4cmis_django_project
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Frontend Changes
```bash
cd j4cmis_frontend
npm run dev  # Hot reload enabled
```

### Create Database Migrations
```bash
cd j4cmis_django_project
source venv/bin/activate
python manage.py makemigrations  # Generate migrations
python manage.py migrate         # Apply migrations
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>

# Find process using port 5173
lsof -i :5173
kill -9 <PID>
```

### Issue: Database Connection Error
```bash
# Reset the database
cd j4cmis_django_project
rm db.sqlite3
source venv/bin/activate
python manage.py migrate
python manage.py bootstrap_roles
```

### Issue: Virtual Environment Issues
```bash
# Recreate virtual environment
cd j4cmis_django_project
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend Can't Connect to Backend
- Verify Django is running on http://127.0.0.1:8000
- Check browser console (F12) for CORS errors
- Ensure both servers are running simultaneously

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Coding Standards
- Python: Follow [PEP 8](https://pep8.org/)
- JavaScript/React: Use ESLint configuration included
- Commit messages: Use clear, descriptive language

---

## 📋 Checklist for First Time Users

- [ ] Clone the repository
- [ ] Install Python 3.9+ and Node.js 20+
- [ ] Set up backend (venv, pip install, migrate)
- [ ] Set up frontend (npm install)
- [ ] Start both servers
- [ ] Access http://localhost:5173/
- [ ] Login with credentials created during setup
- [ ] Explore the admin panel at http://127.0.0.1:8000/admin/
- [ ] Test creating a case
- [ ] Read [Backend README](./j4cmis_django_project/README.md) for architecture details

---

## 📞 Support & Contact

- **Issues:** Report bugs on [GitHub Issues](https://github.com/abilajoshuaalan/J4C-MIS/issues)
- **Discussions:** Use [GitHub Discussions](https://github.com/abilajoshuaalan/J4C-MIS/discussions)
- **Email:** abilajoshuaalan@gmail.com

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with Django, React, and Material-UI
- Designed for the Justice for Children initiative in Uganda
- Special thanks to all contributors and testers

---

**Last Updated:** 2026-07-18  
**Current Status:** ✅ Operational (Development)  
**Version:** 1.0.0
