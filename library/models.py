"""
Models for Library Management System.
Implements the database design from the SRS (Section 7):
  Users → Django built-in auth
  Books, Members, Transactions, Fines
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserProfile(models.Model):
    """
    Extends Django User with a role.
    Roles: admin, librarian, student, faculty (SRS §2.3)
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_staff_role(self):
        return self.role in ('admin', 'librarian')


class Category(models.Model):
    """Book category / genre (FR-206)."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Represents a book in the library catalog (SRS §3.2).
    Tracks ISBN, publisher, edition, category, quantity, and availability.
    """
    book_id = models.CharField(max_length=20, unique=True, verbose_name="Book ID")
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True, default='', verbose_name="ISBN")
    publisher = models.CharField(max_length=200, blank=True, default='')
    edition = models.CharField(max_length=50, blank=True, default='')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='books'
    )
    total_qty = models.PositiveIntegerField(default=1, verbose_name="Total Copies")
    available_qty = models.PositiveIntegerField(default=1, verbose_name="Available Copies")
    added_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['book_id']

    def __str__(self):
        return f"{self.book_id} — {self.title}"

    @property
    def is_available(self):
        return self.available_qty > 0


class Member(models.Model):
    """
    Library member — student or faculty (SRS §3.3).
    Linked to User for login. Has borrowing limits and status.
    """
    MEMBER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    member_id = models.CharField(max_length=20, unique=True, verbose_name="Library Card No.")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member', null=True, blank=True)
    name = models.CharField(max_length=150)
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPE_CHOICES, default='student')
    department = models.CharField(max_length=100, verbose_name="Department / Course")
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['member_id']

    def __str__(self):
        return f"{self.member_id} — {self.name}"

    @property
    def borrow_limit(self):
        """Student: 3 books, Faculty: 5 books (FR-305)."""
        return 5 if self.member_type == 'faculty' else 3

    @property
    def borrow_period_days(self):
        """Student: 14 days, Faculty: 30 days (FR-402)."""
        return 30 if self.member_type == 'faculty' else 14

    def active_issues_count(self):
        """Count of currently held (unreturned) books."""
        return self.transactions.filter(returned=False).count()

    def total_unpaid_fines(self):
        """Sum of all unpaid fines (FR-406)."""
        total = 0
        for txn in self.transactions.filter(returned=False):
            total += txn.fine_amount()
        # Also include unpaid fines from returned books
        for fine in Fine.objects.filter(transaction__member=self, paid=False):
            total += fine.amount
        return total

    def can_borrow(self):
        """Check if member can borrow another book."""
        if self.status != 'active':
            return False, "Member account is inactive."
        if self.active_issues_count() >= self.borrow_limit:
            return False, f"Borrowing limit reached ({self.borrow_limit} books max)."
        if self.total_unpaid_fines() > 100:
            return False, f"Unpaid fines exceed Rs.100 (Rs.{self.total_unpaid_fines()})."
        return True, "OK"


class Transaction(models.Model):
    """
    Represents a book issue/return transaction (SRS §3.4).
    """
    transaction_id = models.CharField(max_length=20, unique=True, verbose_name="Transaction ID")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='transactions')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='issued_transactions', verbose_name="Issued By"
    )

    class Meta:
        ordering = ['-issue_date', '-pk']

    def __str__(self):
        return f"{self.transaction_id}: {self.book.title} → {self.member.name}"

    def is_overdue(self):
        """Check if the book is past due date."""
        if self.returned and self.return_date:
            return self.return_date > self.due_date
        if not self.returned:
            return timezone.now().date() > self.due_date
        return False

    def days_overdue(self):
        """Calculate number of overdue days."""
        if self.returned and self.return_date:
            check = self.return_date
        elif not self.returned:
            check = timezone.now().date()
        else:
            return 0
        delta = (check - self.due_date).days
        return max(delta, 0)

    def fine_amount(self):
        """Calculate fine at Rs.2 per overdue day (FR-501)."""
        return self.days_overdue() * 2


class Fine(models.Model):
    """
    Fine record linked to a transaction (SRS §3.5).
    Created when an overdue book is returned.
    """
    fine_id = models.CharField(max_length=20, unique=True, verbose_name="Fine ID")
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='fine_record')
    amount = models.PositiveIntegerField(default=0, verbose_name="Fine Amount (Rs.)")
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    collected_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fines_collected'
    )

    class Meta:
        ordering = ['-transaction__return_date']

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"{self.fine_id}: Rs.{self.amount} ({status})"
