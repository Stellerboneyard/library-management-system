# 🌐 Deployment & Hosting Guide — Library Management System

## Live Application

| | |
|---|---|
| **Live URL** | [https://library-management-system-c71z.onrender.com](https://library-management-system-c71z.onrender.com) |
| **Login Page** | [https://library-management-system-c71z.onrender.com/login/](https://library-management-system-c71z.onrender.com/login/) |
| **Admin Panel** | [https://library-management-system-c71z.onrender.com/admin/](https://library-management-system-c71z.onrender.com/admin/) |
| **GitHub Repo** | [https://github.com/Stellerboneyard/library-management-system](https://github.com/Stellerboneyard/library-management-system) |
| **Platform** | [Render.com](https://render.com) (Free Tier) |

---

## 🔑 Login Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|-------------|
| **Librarian** | `librarian` | `library123` | Full access — Books, Members, Issue/Return, Fines, Reports |
| **System Admin** | `admin` | `admin123` | Full access + Django Admin Panel (`/admin/`) |

> **Note:** You can also register new accounts via the "Register here" link on the login page, selecting any role (Admin, Librarian, Student, Faculty).

---

## 🗄️ Database Details

### Development (Local)
| Property | Value |
|----------|-------|
| **Engine** | SQLite 3 |
| **File** | `db.sqlite3` (auto-created in project root) |
| **Configuration** | Zero config — built into Python |
| **Why SQLite?** | Lightweight, serverless, no installation needed. Ideal for development and testing. |

### Production (Render.com)
| Property | Value |
|----------|-------|
| **Engine** | PostgreSQL 16 |
| **Provider** | Render Managed PostgreSQL (Free Tier) |
| **Database Name** | `lms_db` |
| **User** | `lms_user` |
| **Connection** | Injected via `DATABASE_URL` environment variable |
| **Max Connections** | 97 (free tier) |
| **Storage** | 1 GB (free tier) |
| **Region** | Oregon, USA |

### How Database Switching Works
In `settings.py`, we use `dj-database-url` to auto-detect the environment:
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',  # Fallback for local dev
        conn_max_age=600,
    )
}
```
- **Locally:** No `DATABASE_URL` env var → uses SQLite
- **On Render:** `DATABASE_URL` is auto-set → uses PostgreSQL

---

## 🏗️ Hosting Architecture

### Platform: Render.com
Render is a cloud platform that auto-deploys from GitHub. Our app uses:

| Component | Type | Plan | Purpose |
|-----------|------|------|---------|
| **Web Service** | Python (Gunicorn) | Free | Runs the Django application |
| **PostgreSQL** | Managed Database | Free | Stores all library data |

### How It Works

```
GitHub Push → Render Auto-Deploy → Build Script → Live App
```

1. **Source Code** lives on GitHub (`main` branch)
2. **Render watches** the repo for commits
3. On push, Render runs `build.sh`:
   ```bash
   pip install -r requirements.txt    # Install dependencies
   python manage.py collectstatic     # Bundle CSS/JS for production
   python manage.py migrate           # Apply database schema
   python manage.py seed_data         # Load sample data
   ```
4. Then starts the app with:
   ```bash
   gunicorn lms.wsgi:application
   ```

### Key Configuration Files

| File | Purpose |
|------|---------|
| `render.yaml` | Render Blueprint — defines services, database, and env vars |
| `build.sh` | Build script run on every deployment |
| `requirements.txt` | Python dependencies for production |
| `Procfile` (implicit) | Start command defined in `render.yaml` |

---

## 🛠️ Technology Stack Explained

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12 | Programming language |
| **Django** | 4.2+ | Web framework (MVC/MVT architecture) |
| **Gunicorn** | 23.0 | Production WSGI HTTP server (replaces `manage.py runserver`) |

### Database
| Technology | Purpose |
|-----------|---------|
| **SQLite** | Local development database (zero-config) |
| **PostgreSQL** | Production database on Render (robust, scalable) |
| **psycopg2-binary** | Python PostgreSQL adapter |
| **dj-database-url** | Parses `DATABASE_URL` env var into Django config |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Page structure (Django Templates) |
| **CSS3** | Custom dark glassmorphism theme |
| **Inter** | Google Font for modern typography |

### Static Files
| Technology | Purpose |
|-----------|---------|
| **WhiteNoise** | Serves CSS/JS directly from Django in production (no Nginx needed) |
| **collectstatic** | Gathers all static files into `staticfiles/` directory |

---

## 🔒 Security Configuration

| Feature | Implementation |
|---------|---------------|
| **Password Hashing** | Django default PBKDF2 with SHA-256 (auto) |
| **CSRF Protection** | Django middleware + `{% csrf_token %}` in all forms |
| **Session Timeout** | 30 minutes (`SESSION_COOKIE_AGE = 1800`) — SRS FR-105 |
| **Secret Key** | Auto-generated by Render (not hardcoded in production) |
| **Debug Mode** | `DEBUG = False` in production |
| **Allowed Hosts** | Restricted to Render hostname in production |
| **CSRF Trusted Origins** | Only `https://*.onrender.com` |

### Environment Variables on Render

| Variable | Value | Purpose |
|----------|-------|---------|
| `SECRET_KEY` | Auto-generated | Django cryptographic key |
| `DEBUG` | `False` | Disables debug mode |
| `DATABASE_URL` | Auto-injected by Render | PostgreSQL connection string |
| `RENDER_EXTERNAL_HOSTNAME` | Auto-set | Used for ALLOWED_HOSTS & CSRF |
| `PYTHON_VERSION` | `3.12.0` | Python runtime version |

---

## 📊 Database Schema (Tables)

The following tables are created by Django migrations:

| Table | Description | Key Fields |
|-------|-------------|------------|
| `library_userprofile` | User roles (extends Django auth) | user_id, role |
| `library_category` | Book categories/genres | name |
| `library_book` | Book catalog | book_id, title, author, isbn, publisher, category, total_qty, available_qty |
| `library_member` | Library members | member_id, name, member_type, department, phone, email, status |
| `library_transaction` | Issue/Return records | transaction_id, book_id, member_id, issue_date, due_date, returned, return_date |
| `library_fine` | Overdue fines | fine_id, transaction_id, amount, paid, paid_date |
| `auth_user` | Django built-in users | username, password (hashed), email, first_name, last_name |

### Entity Relationships
```
User ──(1:1)──> UserProfile (role)
Category ──(1:N)──> Book
Member ──(1:N)──> Transaction
Book ──(1:N)──> Transaction
Transaction ──(1:1)──> Fine
User ──(1:N)──> Transaction (issued_by)
User ──(1:N)──> Fine (collected_by)
```

---

## 📦 Sample Data (Pre-loaded)

### Books (10 titles)
| ID | Title | Author | Category |
|----|-------|--------|----------|
| B001 | Data Structures Using Python | Rance D. Necaise | Computer Science |
| B002 | Introduction to Algorithms | Cormen, Leiserson, Rivest | Computer Science |
| B003 | Database System Concepts | Silberschatz, Korth | Computer Science |
| B004 | Computer Networks | Andrew S. Tanenbaum | Computer Science |
| B005 | Operating System Concepts | Silberschatz, Galvin | Computer Science |
| B006 | Digital Electronics | Morris Mano | Electronics |
| B007 | Engineering Mathematics | B.S. Grewal | Mathematics |
| B008 | Software Engineering | Roger S. Pressman | Computer Science |
| B009 | Artificial Intelligence | Stuart Russell, Peter Norvig | Computer Science |
| B010 | Python Programming | Mark Lutz | Computer Science |

### Members (6 members)
| Card No. | Name | Type | Department |
|----------|------|------|------------|
| LIB-2026-001 | Aryan Kulhari | Student | CSE |
| LIB-2026-002 | Priya Verma | Student | CSE |
| LIB-2026-003 | Rahul Gupta | Student | IT |
| LIB-2026-004 | Sneha Jain | Student | ECE |
| LIB-2026-005 | Dr. Sharma | Faculty | CSE |
| LIB-2026-006 | Ayush Raj | Student | CSE |

### Transactions (8 records)
| ID | Type | Status |
|----|------|--------|
| T001 | Active issue | ✅ On time |
| T002 | Active issue | ⚠️ Overdue (student) |
| T003 | Active issue | ✅ On time (faculty, 30-day period) |
| T004 | Returned | ✅ Returned on time |
| T005 | Returned late | ⚠️ Fine ₹8 (unpaid) |
| T006 | Active issue | ⚠️ Overdue (faculty) |
| T007 | Active issue | ✅ On time |
| T008 | Returned late | ✅ Fine ₹12 (paid) |

---

## 🚀 How to Run Locally

```bash
# 1. Clone
git clone https://github.com/Stellerboneyard/library-management-system.git
cd library-management-system

# 2. Virtual Environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Database Setup
python manage.py makemigrations library
python manage.py migrate

# 5. Load Sample Data
python manage.py seed_data

# 6. Run Server
python manage.py runserver

# 7. Open http://127.0.0.1:8000/login/
#    Login: librarian / library123
```

---

## 👥 Team

| Name | Role | Module |
|------|------|--------|
| Aryan Kulhari | Team Leader | Project Setup, Dashboard, CSS Theme, Deployment |
| Aryan Singh Rathore | Developer | Authentication (Login, Register, Roles) |
| Aryan Raj | Developer | Book Management, Categories, Search |
| Aryan Prashad | Developer | Member Management, Business Rules |
| Ayush Raj | Developer | Issue/Return System, Transactions |
| Abhi Jain | Developer | Fine Management, Reports, Admin |

**B.Tech CSE — Software Engineering Lab, Session 2025–26**
**Arya College of Engineering & I.T., Jaipur**
