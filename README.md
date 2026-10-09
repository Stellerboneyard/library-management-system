# 📚 Library Management System

A web-based Library Management System built with **Django** for automating college library operations — book cataloging, member registration, book issuing/returning, fine calculation, and report generation.

**B.Tech CSE — Software Engineering Lab Project**
Arya College of Engineering & I.T., Jaipur

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **Authentication** | Login, register, role-based access (Admin, Librarian, Student, Faculty) |
| **Book Management** | Full CRUD with ISBN, publisher, edition, category, quantity tracking |
| **Member Management** | Student/Faculty registration with library cards and borrowing limits |
| **Issue & Return** | Issue books with auto due-dates (Students: 14d, Faculty: 30d), return processing |
| **Fine Management** | Auto-calculate fines @ ₹2/day, payment tracking, block if fines > ₹100 |
| **Search & Catalog** | Multi-filter search by title, author, ISBN, category, availability |
| **Reports** | Overdue books, popular books, member activity, transaction history |
| **Categories** | Organize books by genre/department |

## 🛠️ Tech Stack

- **Backend:** Python, Django 4.2+
- **Database:** SQLite (development)
- **Frontend:** HTML5, CSS3 (custom dark glassmorphism theme), Django Templates
- **Font:** Inter (Google Fonts)

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Stellerboneyard/library-management-system.git
cd library-management-system
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations library
python manage.py migrate
```

### 5. Load sample data
```bash
python manage.py seed_data
```

### 6. Start the server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Librarian | `librarian` | `library123` |
| Admin | `admin` | `admin123` |

## 📁 Project Structure

```
library-management-system/
├── lms/                    # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── library/                # Main app
│   ├── models.py           # Book, Member, Transaction, Fine, Category
│   ├── views.py            # All CRUD + business logic
│   ├── forms.py            # Validated forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin config
│   └── management/
│       └── commands/
│           └── seed_data.py  # Sample data loader
├── templates/              # HTML templates
│   ├── base.html           # Base layout with sidebar
│   └── library/            # All page templates
├── static/
│   └── css/
│       └── style.css       # Dark glassmorphism theme
├── manage.py
├── requirements.txt
└── README.md
```

## 📋 Business Rules (from SRS)

- **Borrowing Limits:** Students: 3 books, Faculty: 5 books
- **Borrowing Period:** Students: 14 days, Faculty: 30 days
- **Fine Rate:** ₹2 per day for overdue books
- **Fine Block:** Cannot issue if unpaid fines exceed ₹100
- **Duplicate Prevention:** Cannot issue same book twice to same member

## 👥 Team

- **Team Leader:** Aryan Kulhari
- **Members:** Aryan Singh Rathore, Aryan Raj, Aryan Prashad, Ayush Raj, Abhi Jain

## 📄 License

This project is developed for academic purposes at Arya College of Engineering & I.T., Jaipur.
