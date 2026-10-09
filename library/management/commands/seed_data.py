"""
Management command to populate the LMS with sample data matching the SRS.
Creates a librarian user, categories, books, members, and transactions.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from library.models import Book, Member, Transaction, Fine, Category, UserProfile


class Command(BaseCommand):
    help = 'Populate database with sample library data.'

    def handle(self, *args, **options):
        # Clear data
        Fine.objects.all().delete()
        Transaction.objects.all().delete()
        Member.objects.all().delete()
        Book.objects.all().delete()
        Category.objects.all().delete()

        # ── Create Librarian user if not exists ──
        if not User.objects.filter(username='librarian').exists():
            user = User.objects.create_user(
                username='librarian', password='library123',
                first_name='Librarian', last_name='Admin',
                email='librarian@arya.edu.in',
            )
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'librarian'})
            self.stdout.write(f'  🔑 Created user: librarian / library123')

        # Also create admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', password='admin123',
                first_name='System', last_name='Admin',
                email='admin@arya.edu.in',
            )
            UserProfile.objects.get_or_create(user=admin, defaults={'role': 'admin'})
            self.stdout.write(f'  🔑 Created superuser: admin / admin123')

        # ── Categories ──
        categories = {}
        for name in ['Computer Science', 'Mathematics', 'Electronics', 'Physics', 'Literature', 'Engineering']:
            cat = Category.objects.create(name=name)
            categories[name] = cat
            self.stdout.write(f'  🏷️  Category: {name}')

        # ── Books (matching SRS scope) ──
        books_data = [
            ('B001', 'Data Structures Using Python', 'Rance D. Necaise', '978-0-470-61822-1', 'Wiley', '1st Ed.', 'Computer Science', 3),
            ('B002', 'Introduction to Algorithms', 'Cormen, Leiserson, Rivest', '978-0-262-03384-8', 'MIT Press', '3rd Ed.', 'Computer Science', 2),
            ('B003', 'Database System Concepts', 'Silberschatz, Korth, Sudarshan', '978-0-07-352332-3', 'McGraw-Hill', '7th Ed.', 'Computer Science', 2),
            ('B004', 'Computer Networks', 'Andrew S. Tanenbaum', '978-0-13-212695-3', 'Pearson', '5th Ed.', 'Computer Science', 2),
            ('B005', 'Operating System Concepts', 'Silberschatz, Galvin, Gagne', '978-1-118-06333-0', 'Wiley', '10th Ed.', 'Computer Science', 3),
            ('B006', 'Digital Electronics', 'Morris Mano', '978-0-13-277420-8', 'Pearson', '6th Ed.', 'Electronics', 2),
            ('B007', 'Engineering Mathematics', 'B.S. Grewal', '978-81-7409-195-5', 'Khanna', '44th Ed.', 'Mathematics', 4),
            ('B008', 'Software Engineering', 'Roger S. Pressman', '978-0-07-802212-8', 'McGraw-Hill', '8th Ed.', 'Computer Science', 2),
            ('B009', 'Artificial Intelligence', 'Stuart Russell, Peter Norvig', '978-0-13-604259-4', 'Pearson', '4th Ed.', 'Computer Science', 1),
            ('B010', 'Python Programming', 'Mark Lutz', '978-1-449-35573-9', 'O\'Reilly', '5th Ed.', 'Computer Science', 3),
        ]
        books = {}
        for bid, title, author, isbn, pub, ed, cat_name, qty in books_data:
            b = Book.objects.create(
                book_id=bid, title=title, author=author, isbn=isbn,
                publisher=pub, edition=ed, category=categories[cat_name],
                total_qty=qty, available_qty=qty,
            )
            books[bid] = b
            self.stdout.write(f'  📖 {b}')

        # ── Members ──
        members_data = [
            ('LIB-2026-001', 'Aryan Kulhari', 'student', 'CSE', '9876543210', 'aryan.k@arya.edu.in'),
            ('LIB-2026-002', 'Priya Verma', 'student', 'CSE', '9123456780', 'priya.v@arya.edu.in'),
            ('LIB-2026-003', 'Rahul Gupta', 'student', 'IT', '9988776655', 'rahul.g@arya.edu.in'),
            ('LIB-2026-004', 'Sneha Jain', 'student', 'ECE', '9012345678', 'sneha.j@arya.edu.in'),
            ('LIB-2026-005', 'Dr. Sharma', 'faculty', 'CSE', '9876501234', 'dr.sharma@arya.edu.in'),
            ('LIB-2026-006', 'Ayush Raj', 'student', 'CSE', '9876512345', 'ayush.r@arya.edu.in'),
        ]
        members = {}
        for mid, name, mtype, dept, phone, email in members_data:
            m = Member.objects.create(
                member_id=mid, name=name, member_type=mtype,
                department=dept, phone=phone, email=email,
            )
            members[mid] = m
            self.stdout.write(f'  👤 {m} ({mtype})')

        today = timezone.now().date()

        # ── Transactions ──
        # Active, on-time
        t1 = Transaction.objects.create(
            transaction_id='T001', book=books['B001'], member=members['LIB-2026-001'],
            issue_date=today - timedelta(days=5), due_date=today + timedelta(days=9),
        )
        books['B001'].available_qty -= 1; books['B001'].save()
        self.stdout.write(f'  📤 {t1}')

        # Active, overdue (student)
        t2 = Transaction.objects.create(
            transaction_id='T002', book=books['B002'], member=members['LIB-2026-002'],
            issue_date=today - timedelta(days=22), due_date=today - timedelta(days=8),
        )
        books['B002'].available_qty -= 1; books['B002'].save()
        self.stdout.write(f'  📤 {t2} (overdue)')

        # Active, on-time (faculty, 30-day period)
        t3 = Transaction.objects.create(
            transaction_id='T003', book=books['B008'], member=members['LIB-2026-005'],
            issue_date=today - timedelta(days=10), due_date=today + timedelta(days=20),
        )
        books['B008'].available_qty -= 1; books['B008'].save()
        self.stdout.write(f'  📤 {t3} (faculty)')

        # Returned on-time, no fine
        t4 = Transaction.objects.create(
            transaction_id='T004', book=books['B003'], member=members['LIB-2026-003'],
            issue_date=today - timedelta(days=30), due_date=today - timedelta(days=16),
            returned=True, return_date=today - timedelta(days=18),
        )
        self.stdout.write(f'  ✅ {t4} (returned)')

        # Returned late, fine generated
        t5 = Transaction.objects.create(
            transaction_id='T005', book=books['B004'], member=members['LIB-2026-001'],
            issue_date=today - timedelta(days=28), due_date=today - timedelta(days=14),
            returned=True, return_date=today - timedelta(days=10),
        )
        fine_amt = t5.fine_amount()
        if fine_amt > 0:
            Fine.objects.create(fine_id='F001', transaction=t5, amount=fine_amt, paid=False)
        self.stdout.write(f'  ⚠️  {t5} (late, fine ₹{fine_amt})')

        # Active overdue (faculty)
        t6 = Transaction.objects.create(
            transaction_id='T006', book=books['B009'], member=members['LIB-2026-005'],
            issue_date=today - timedelta(days=40), due_date=today - timedelta(days=10),
        )
        books['B009'].available_qty -= 1; books['B009'].save()
        self.stdout.write(f'  📤 {t6} (faculty overdue)')

        # Another active for student
        t7 = Transaction.objects.create(
            transaction_id='T007', book=books['B010'], member=members['LIB-2026-004'],
            issue_date=today - timedelta(days=3), due_date=today + timedelta(days=11),
        )
        books['B010'].available_qty -= 1; books['B010'].save()
        self.stdout.write(f'  📤 {t7}')

        # Returned, fine paid
        t8 = Transaction.objects.create(
            transaction_id='T008', book=books['B006'], member=members['LIB-2026-006'],
            issue_date=today - timedelta(days=35), due_date=today - timedelta(days=21),
            returned=True, return_date=today - timedelta(days=15),
        )
        fine8 = t8.fine_amount()
        if fine8 > 0:
            Fine.objects.create(
                fine_id='F002', transaction=t8, amount=fine8,
                paid=True, paid_date=today - timedelta(days=14),
            )
        self.stdout.write(f'  ✅ {t8} (returned, fine paid ₹{fine8})')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeded: {Book.objects.count()} books, '
            f'{Member.objects.count()} members, '
            f'{Category.objects.count()} categories, '
            f'{Transaction.objects.count()} transactions, '
            f'{Fine.objects.count()} fines.'
        ))
        self.stdout.write(self.style.SUCCESS(
            '\n🔑 Login credentials:\n'
            '   Librarian: librarian / library123\n'
            '   Admin:     admin / admin123'
        ))
