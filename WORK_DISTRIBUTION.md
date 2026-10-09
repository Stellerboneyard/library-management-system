# 📚 Library Management System — Work Distribution & Explanation

## Team Members — Arya College of Engineering & IT, CSE

| # | Name | Role | Modules Assigned |
|---|------|------|-----------------|
| 1 | **Aryan Kulhari** | Team Leader | Project Setup, Settings, Dashboard, Integration & Deployment |
| 2 | **Aryan Singh Rathore** | Developer | User Authentication Module (Login, Register, Roles) |
| 3 | **Aryan Raj** | Developer | Book Management & Category Module |
| 4 | **Aryan Prashad** | Developer | Member Management Module |
| 5 | **Ayush Raj** | Developer | Book Issue & Return Module |
| 6 | **Abhi Jain** | Developer | Fine Management & Reports Module |

---

## 1. Aryan Kulhari — Team Leader
### **Project Setup, Dashboard, Integration & Deployment**

### Files Responsible For:
- [`manage.py`](manage.py) — Django entry point
- [`lms/settings.py`](lms/settings.py) — Project configuration
- [`lms/urls.py`](lms/urls.py) — Root URL routing
- [`templates/base.html`](templates/base.html) — Base layout template
- [`templates/library/dashboard.html`](templates/library/dashboard.html) — Dashboard template
- [`static/css/style.css`](static/css/style.css) — Global stylesheet
- [`library/management/commands/seed_data.py`](library/management/commands/seed_data.py) — Sample data loader
- [`.gitignore`](.gitignore), [`requirements.txt`](requirements.txt), [`README.md`](README.md) — Project documentation

### What I Did (Explanation for Viva):

> **"As the team leader, I was responsible for setting up the entire Django project structure, configuring the settings, and creating the base template that all other pages extend. I also built the dashboard and handled the final integration and deployment to GitHub."**

#### 1. Project Setup (`lms/settings.py`)
- Created the Django project using `django-admin startproject lms`
- Configured the **SQLite database** (Section 7 of SRS — lightweight, no external DB setup needed)
- Registered the `library` app in `INSTALLED_APPS`
- Set up the **template directory** (`templates/`) and **static files directory** (`static/`)
- Configured **session timeout to 30 minutes** (`SESSION_COOKIE_AGE = 1800`) as per **FR-105**
- Set `TIME_ZONE = 'Asia/Kolkata'` for Indian Standard Time
- Configured `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL` for authentication flow
- Mapped Django message tags to CSS class names for styled alerts

#### 2. Base Template (`templates/base.html`)
- Designed a **sidebar navigation layout** with sections for Overview, Catalog, People, Transactions, and Analytics
- Implemented **active link highlighting** using Django's `request.resolver_match.url_name`
- Added a **user info panel** at the bottom of sidebar showing logged-in user's name and role
- Included the **Django messages framework** for success/error/warning notifications with emoji icons
- Used `{% load static %}` to link the CSS stylesheet

#### 3. Dashboard (`views.py → dashboard()` + `dashboard.html`)
- Queries the database for **6 key statistics**: Total Books, Active Members, Books Issued, Overdue Count, Categories, Unpaid Fines
- Calculates overdue count by iterating through active transactions and calling `is_overdue()`
- Displays **Quick Action buttons** for common tasks (Add Book, Register Member, Issue Book, Search, Reports)
- Shows an **Overdue Alert table** if any books are overdue
- Shows a **Recent Issues table** with the latest 5 active transactions

#### 4. CSS Stylesheet (`static/css/style.css`)
- Designed a **dark glassmorphism theme** with CSS custom properties (design tokens)
- Used **Inter** font from Google Fonts for modern typography
- Created reusable component classes: `.stat-card`, `.card`, `.badge`, `.btn`, `.form-input`, `.alert`
- Added **ambient background gradients** using `radial-gradient` on `body::before`
- Implemented **hover animations** (`translateY`, `box-shadow` transitions) on cards and buttons
- Added **responsive breakpoints** at 768px and 480px for tablet/mobile

#### 5. GitHub Deployment
- Initialized Git repository, created `.gitignore` for Python/Django
- Created public repository on GitHub using `gh repo create`
- Pushed all code to `main` branch

---

## 2. Aryan Singh Rathore
### **User Authentication Module (SRS §3.1)**

### Files Responsible For:
- [`library/models.py`](library/models.py) — `UserProfile` model (lines 14–31)
- [`library/forms.py`](library/forms.py) — `LoginForm`, `RegisterForm` (lines 13–55)
- [`library/views.py`](library/views.py) — `login_view()`, `register_view()`, `logout_view()`, helper functions (lines 24–85)
- [`library/urls.py`](library/urls.py) — Auth URL patterns (lines 6–8)
- [`templates/library/login.html`](templates/library/login.html) — Login page
- [`templates/library/register.html`](templates/library/register.html) — Registration page

### What I Did (Explanation for Viva):

> **"I implemented the complete user authentication system — login, registration, logout, and role-based access control. I used Django's built-in authentication framework and extended it with a UserProfile model to support four user roles as defined in the SRS."**

#### 1. UserProfile Model
```python
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
```
- Extended Django's built-in `User` model using a **OneToOneField** relationship
- Defined **4 user roles** as per SRS §2.3: Admin, Librarian, Student, Faculty
- Added `is_staff_role` property to check if a user is admin or librarian
- Django's `User` model already handles **password hashing** (bcrypt/PBKDF2) as per **FR-106/NFR-05**

#### 2. Login System (FR-102)
- Used Django's `AuthenticationForm` as base, customized with styled widgets
- `login_view()` authenticates using `form.get_user()` and calls `login()` to create session
- On success, redirects to dashboard with a welcome message
- If already authenticated, redirects to dashboard automatically

#### 3. Registration System (FR-101)
- Custom `RegisterForm` with fields: username, first_name, last_name, email, password, role
- **Validation**: checks for duplicate username, enforces minimum 6-character password
- Creates `User` with `create_user()` (auto-hashes password) and `UserProfile` with selected role
- Auto-logs in the user after successful registration

#### 4. Role-Based Access Control (FR-103)
- Helper function `_is_staff(user)` checks if user's role is `admin` or `librarian`
- Used as a guard in every view that modifies data — returns "Permission denied" for unauthorized users
- The `@login_required` decorator redirects unauthenticated users to the login page

#### 5. Session Management (FR-105)
- Configured in `settings.py`: `SESSION_COOKIE_AGE = 1800` (30-minute timeout)
- `SESSION_SAVE_EVERY_REQUEST = True` resets the timer on each page load
- `logout_view()` calls `logout()` which destroys the session and flushes session data

---

## 3. Aryan Raj
### **Book Management & Category Module (SRS §3.2, §3.6)**

### Files Responsible For:
- [`library/models.py`](library/models.py) — `Category` model (lines 34–43), `Book` model (lines 46–76)
- [`library/forms.py`](library/forms.py) — `BookForm`, `CategoryForm` (lines 59–89, 137–142)
- [`library/views.py`](library/views.py) — `book_list()`, `book_add()`, `book_edit()`, `book_delete()`, `category_list()`, `category_delete()` (lines 95–167, 310–340)
- [`templates/library/book_list.html`](templates/library/book_list.html) — Book catalog page
- [`templates/library/book_form.html`](templates/library/book_form.html) — Add/Edit book form
- [`templates/library/category_list.html`](templates/library/category_list.html) — Category management page
- [`templates/library/confirm_delete.html`](templates/library/confirm_delete.html) — Delete confirmation (shared)

### What I Did (Explanation for Viva):

> **"I built the book management and category modules — the core of the library catalog. This includes full CRUD operations for books and categories, advanced search with multiple filters, and availability tracking."**

#### 1. Book Model (FR-201, FR-204)
```python
class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    total_qty = models.PositiveIntegerField(default=1)
    available_qty = models.PositiveIntegerField(default=1)
```
- Stores all book metadata: title, author, ISBN, publisher, edition, category
- **`ForeignKey` to Category** with `SET_NULL` — if a category is deleted, books remain (just lose their category)
- Tracks `total_qty` (total copies owned) and `available_qty` (currently in library)
- `is_available` property returns `True` if `available_qty > 0`

#### 2. Category Model (FR-206)
- Simple model with a unique `name` field
- Books are categorized by genre/department (Computer Science, Mathematics, Electronics, etc.)
- Category list page includes an **inline add form** and shows **book count** per category using `annotate(book_count=Count('books'))`

#### 3. Book Search & Filtering (FR-601, FR-602, FR-603)
```python
def book_list(request):
    books = Book.objects.select_related('category').all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query) |
            Q(isbn__icontains=query) | Q(book_id__icontains=query) |
            Q(publisher__icontains=query)
        )
    if cat_filter:
        books = books.filter(category__id=cat_filter)
    if avail_filter == 'yes':
        books = books.filter(available_qty__gt=0)
```
- **Multi-field text search** using Django's `Q` objects with `OR` logic (`|`)
- **Category filter** dropdown populated from `Category.objects.all()`
- **Availability filter** (Available / All Issued)
- Used `select_related('category')` to **avoid N+1 query problem** — fetches category in single JOIN query

#### 4. BookForm with Auto-Available (FR-201)
- On creation (when `book.pk` is `None`), automatically sets `available_qty = total_qty`
- This ensures newly added books start with all copies available

---

## 4. Aryan Prashad
### **Member Management Module (SRS §3.3)**

### Files Responsible For:
- [`library/models.py`](library/models.py) — `Member` model (lines 79–130)
- [`library/forms.py`](library/forms.py) — `MemberForm` (lines 93–105)
- [`library/views.py`](library/views.py) — `member_list()`, `member_add()`, `member_edit()`, `member_delete()`, `member_detail()` (lines 170–235)
- [`templates/library/member_list.html`](templates/library/member_list.html) — Member list page
- [`templates/library/member_form.html`](templates/library/member_form.html) — Add/Edit member form
- [`templates/library/member_detail.html`](templates/library/member_detail.html) — Member profile page

### What I Did (Explanation for Viva):

> **"I developed the member management module which handles registration, profile management, and detailed member views. The key challenge was implementing different borrowing limits and periods for students and faculty, and the business rule that blocks borrowing when fines exceed ₹100."**

#### 1. Member Model (FR-301, FR-302, FR-305)
```python
class Member(models.Model):
    MEMBER_TYPE_CHOICES = [('student', 'Student'), ('faculty', 'Faculty')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    member_id = models.CharField(max_length=20, unique=True)  # Library Card No.
    name = models.CharField(max_length=150)
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPE_CHOICES)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
```

#### 2. Business Rules — Properties & Methods
- **`borrow_limit`** property — Returns `3` for students, `5` for faculty (FR-305)
- **`borrow_period_days`** property — Returns `14` for students, `30` for faculty (FR-402)
- **`active_issues_count()`** — Counts unreturned books using `self.transactions.filter(returned=False).count()`
- **`total_unpaid_fines()`** — Sums all unpaid fines from active and returned transactions
- **`can_borrow()`** — The central validation method that checks:
  1. Is member status `active`? (FR-304)
  2. Has member reached their borrowing limit? (FR-405)
  3. Do unpaid fines exceed ₹100? (FR-406)

```python
def can_borrow(self):
    if self.status != 'active':
        return False, "Member account is inactive."
    if self.active_issues_count() >= self.borrow_limit:
        return False, f"Borrowing limit reached ({self.borrow_limit} books max)."
    if self.total_unpaid_fines() > 100:
        return False, f"Unpaid fines exceed Rs.100."
    return True, "OK"
```

#### 3. Member Detail Page
- Shows member **avatar** (first letter of name), profile info, and status badges
- Displays a **detail grid** with Library Card, Phone, Email, Join Date, Active Issues (X/limit), Unpaid Fines
- Includes complete **borrowing history table** with all transactions for that member
- Uses `select_related('book')` on transactions for efficient querying

#### 4. Member List with Search
- Search by name, member_id, department, or email using `Q` objects
- Filter by member type (Student / Faculty) dropdown
- Shows **active issues count** with color-coded badges (green/blue/warning based on how close to limit)

---

## 5. Ayush Raj
### **Book Issue & Return Module (SRS §3.4)**

### Files Responsible For:
- [`library/models.py`](library/models.py) — `Transaction` model (lines 133–174)
- [`library/forms.py`](library/forms.py) — `IssueBookForm`, `ReturnBookForm` (lines 109–132)
- [`library/views.py`](library/views.py) — `issue_list()`, `issue_book()`, `return_book()`, `transaction_history()` (lines 238–290)
- [`templates/library/issue_list.html`](templates/library/issue_list.html) — Active issues page
- [`templates/library/issue_form.html`](templates/library/issue_form.html) — Issue book form
- [`templates/library/return_form.html`](templates/library/return_form.html) — Return book form
- [`templates/library/transaction_history.html`](templates/library/transaction_history.html) — Full history page

### What I Did (Explanation for Viva):

> **"I built the core transaction engine — the issue and return system. This is the most critical module as it ties together books and members, enforces all business rules, manages availability in real-time, and calculates overdue status and fines."**

#### 1. Transaction Model (FR-401, FR-407)
```python
class Transaction(models.Model):
    transaction_id = models.CharField(max_length=20, unique=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='transactions')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```
- Links `Book` and `Member` via **ForeignKey** relationships
- `related_name='transactions'` allows reverse lookups: `book.transactions.all()`, `member.transactions.all()`
- Tracks who issued the book (`issued_by`) for audit trail

#### 2. Overdue & Fine Calculation Methods
```python
def is_overdue(self):
    if self.returned and self.return_date:
        return self.return_date > self.due_date
    if not self.returned:
        return timezone.now().date() > self.due_date
    return False

def fine_amount(self):
    return self.days_overdue() * 2  # Rs.2 per day (FR-501)
```
- `is_overdue()` works for both **active** (compares today vs due_date) and **returned** (compares return_date vs due_date) transactions
- `days_overdue()` uses `max(delta, 0)` to never return negative days
- `fine_amount()` multiplies overdue days by ₹2

#### 3. Issue Book Process (FR-401, FR-402, FR-405)
```python
def issue_book(request):
    # 1. Validate form (checks can_borrow(), duplicate issue)
    # 2. Generate sequential transaction ID (T001, T002, ...)
    # 3. Calculate due_date based on member type (14d or 30d)
    # 4. Create Transaction record
    # 5. Decrement book.available_qty
```
- **Auto-generates transaction IDs** sequentially using `_next_id('T', Transaction, 'transaction_id')`
- **Due date is automatic** — `issue_date + timedelta(days=member.borrow_period_days)` (14 or 30 days)
- **Decrements available copies** on the Book model after issue

#### 4. IssueBookForm Validation
- Queryset only shows **active members** and **books with available_qty > 0**
- Calls `member.can_borrow()` to enforce borrowing limit and fine block
- Checks for **duplicate active issue** — prevents issuing the same book twice to the same member

#### 5. Return Book Process (FR-403)
- Sets `returned = True` and `return_date`
- **Increments `book.available_qty`** to reflect the return
- If overdue, **automatically creates a Fine record** with calculated amount
- Shows appropriate success or warning message

---

## 6. Abhi Jain
### **Fine Management & Reports Module (SRS §3.5, §3.7)**

### Files Responsible For:
- [`library/models.py`](library/models.py) — `Fine` model (lines 177–195)
- [`library/forms.py`](library/forms.py) — `PayFineForm` (lines 135–141)
- [`library/views.py`](library/views.py) — `fine_list()`, `fine_pay()`, `reports()`, `report_overdue()`, `report_popular()`, `report_member_activity()` (lines 293–345)
- [`templates/library/fine_list.html`](templates/library/fine_list.html) — Fine management page
- [`templates/library/fine_pay.html`](templates/library/fine_pay.html) — Fine payment page
- [`templates/library/reports.html`](templates/library/reports.html) — Reports dashboard
- [`templates/library/report_overdue.html`](templates/library/report_overdue.html) — Overdue report
- [`templates/library/report_popular.html`](templates/library/report_popular.html) — Popular books report
- [`templates/library/report_members.html`](templates/library/report_members.html) — Member activity report
- [`library/admin.py`](library/admin.py) — Django admin registration for all models

### What I Did (Explanation for Viva):

> **"I built the fine management system and all the report generation modules. The fine system automatically tracks overdue penalties and allows librarians to record payments. The reports module provides insights through overdue reports, popular books rankings, and member activity analysis."**

#### 1. Fine Model (FR-501, FR-503)
```python
class Fine(models.Model):
    fine_id = models.CharField(max_length=20, unique=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='fine_record')
    amount = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```
- **OneToOneField to Transaction** — each transaction can have at most one fine
- Tracks payment status (`paid`), payment date, and who collected it
- Fine is created automatically when an overdue book is returned (in `return_book()` view)
- Fine rate: **₹2 per overdue day** (FR-501)

#### 2. Fine Management Page (FR-502, FR-503)
- Shows **two stat cards**: Total Unpaid Fines and Total Collected using `aggregate(Sum('amount'))`
- **Filter tabs**: All / Unpaid / Paid using URL query parameter `?status=unpaid`
- Table displays Fine ID, Member, Book, Amount, Status, Paid Date, and Collect action
- `fine_pay()` view records payment with confirmation checkbox, sets `paid=True`, `paid_date`, and `collected_by`

#### 3. Reports Dashboard (SRS §3.7)
- Central page with **5 report cards** linking to individual reports
- Each card has an icon, title, description, and action button

#### 4. Overdue Books Report (FR-702)
```python
def report_overdue(request):
    overdue = []
    for txn in Transaction.objects.filter(returned=False).select_related('book', 'member'):
        if txn.is_overdue():
            overdue.append(txn)
```
- Filters active transactions and checks `is_overdue()` on each
- Shows book, member, type, issue date, due date, days overdue, fine amount
- Includes direct "Return" action button for each overdue book

#### 5. Most Popular Books Report (FR-703)
```python
def report_popular(request):
    popular = Book.objects.annotate(
        issue_count=Count('transactions')
    ).order_by('-issue_count')[:10]
```
- Uses Django's **`annotate()`** with `Count()` aggregation to count transactions per book
- Orders by highest issue count, limits to top 10
- Shows rank, book details, category, issue count, and availability

#### 6. Member Activity Report (FR-704)
```python
members = Member.objects.annotate(
    total_issues=Count('transactions'),
    active_issues=Count('transactions', filter=Q(transactions__returned=False)),
).order_by('-total_issues')
```
- Uses **conditional aggregation** — `Count()` with `filter=Q(...)` to count only active (unreturned) issues
- Shows total lifetime issues and current active issues per member
- Sorted by most active members first

#### 7. Django Admin Registration
- Registered all 6 models (`UserProfile`, `Category`, `Book`, `Member`, `Transaction`, `Fine`) in Django admin
- Configured `list_display`, `search_fields`, `list_filter` for each model
- Accessible at `/admin/` for administrative operations

---

## 📊 Work Distribution Summary

```
┌──────────────────────┬──────────────────────────────────────────┬───────────────┐
│ Member               │ Module                                   │ Files Created │
├──────────────────────┼──────────────────────────────────────────┼───────────────┤
│ Aryan Kulhari        │ Setup, Dashboard, CSS, Deployment        │ 9 files       │
│ Aryan Singh Rathore  │ Authentication (Login/Register/Roles)    │ 6 files       │
│ Aryan Raj            │ Book CRUD, Categories, Search/Filter     │ 7 files       │
│ Aryan Prashad        │ Member CRUD, Detail View, Validation     │ 6 files       │
│ Ayush Raj            │ Issue, Return, Transaction History       │ 7 files       │
│ Abhi Jain            │ Fines, Reports (Overdue/Popular/Members) │ 9 files       │
└──────────────────────┴──────────────────────────────────────────┴───────────────┘
```

> **Total: 44 files · 3,784 lines of code**
> **GitHub: https://github.com/Stellerboneyard/library-management-system**
