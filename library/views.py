"""
Views for Library Management System.
Implements all modules from the SRS:
  Auth, Dashboard, Books, Members, Issue/Return, Fines, Reports.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import Book, Member, Transaction, Fine, Category, UserProfile
from .forms import (
    LoginForm, RegisterForm, BookForm, MemberForm,
    IssueBookForm, ReturnBookForm, PayFineForm, CategoryForm,
)


# ─── Helpers ──────────────────────────────────────────────────

def _get_role(user):
    """Get user role string or 'guest'."""
    try:
        return user.profile.role
    except (UserProfile.DoesNotExist, AttributeError):
        return 'guest'


def _is_staff(user):
    """Check if user is admin or librarian."""
    return _get_role(user) in ('admin', 'librarian')


def _next_id(prefix, model, field):
    """Generate next sequential ID like T001, F001, etc."""
    last = model.objects.order_by('-pk').first()
    num = (last.pk + 1) if last else 1
    return f"{prefix}{num:03d}"


# ─── Auth Views ───────────────────────────────────────────────

def login_view(request):
    """User login (FR-102)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'Welcome back, {request.user.get_full_name() or request.user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'library/login.html', {'form': form})


def register_view(request):
    """User registration (FR-101)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data.get('last_name', ''),
            )
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'library/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── Dashboard ────────────────────────────────────────────────

@login_required
def dashboard(request):
    """Role-specific dashboard with summary cards (SRS §4.1)."""
    total_books = Book.objects.count()
    total_members = Member.objects.filter(status='active').count()
    active_issues = Transaction.objects.filter(returned=False).count()

    overdue_issues = []
    for txn in Transaction.objects.filter(returned=False).select_related('book', 'member'):
        if txn.is_overdue():
            overdue_issues.append(txn)

    total_categories = Category.objects.count()
    unpaid_fines_total = Fine.objects.filter(paid=False).aggregate(s=Sum('amount'))['s'] or 0

    recent_transactions = Transaction.objects.filter(
        returned=False
    ).select_related('book', 'member')[:5]

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'active_issues': active_issues,
        'overdue_count': len(overdue_issues),
        'total_categories': total_categories,
        'unpaid_fines_total': unpaid_fines_total,
        'overdue_issues': overdue_issues[:5],
        'recent_transactions': recent_transactions,
        'user_role': _get_role(request.user),
    }
    return render(request, 'library/dashboard.html', context)


# ─── Book Views ───────────────────────────────────────────────

@login_required
def book_list(request):
    """Display all books with search (FR-601, FR-602, FR-603)."""
    query = request.GET.get('q', '').strip()
    cat_filter = request.GET.get('cat', '').strip()
    avail_filter = request.GET.get('avail', '').strip()

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
    elif avail_filter == 'no':
        books = books.filter(available_qty=0)

    categories = Category.objects.all()

    context = {
        'books': books,
        'query': query,
        'cat_filter': cat_filter,
        'avail_filter': avail_filter,
        'categories': categories,
    }
    return render(request, 'library/book_list.html', context)


@login_required
def book_add(request):
    """Add a new book (FR-201)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('book_list')
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Add'})


@login_required
def book_edit(request, pk):
    """Edit a book (FR-202)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated.')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Edit'})


@login_required
def book_delete(request, pk):
    """Delete a book (FR-203)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('book_list')
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted.')
        return redirect('book_list')
    return render(request, 'library/confirm_delete.html', {'object': book, 'type': 'Book'})


# ─── Member Views ─────────────────────────────────────────────

@login_required
def member_list(request):
    """Display all members (FR-301)."""
    query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()

    members_qs = Member.objects.all()
    if query:
        members_qs = members_qs.filter(
            Q(name__icontains=query) | Q(member_id__icontains=query) |
            Q(department__icontains=query) | Q(email__icontains=query)
        )
    if type_filter:
        members_qs = members_qs.filter(member_type=type_filter)

    context = {'members': members_qs, 'query': query, 'type_filter': type_filter}
    return render(request, 'library/member_list.html', context)


@login_required
def member_add(request):
    """Register a new member (FR-301, FR-302)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('member_list')
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member "{member.name}" registered with card {member.member_id}!')
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'library/member_form.html', {'form': form, 'action': 'Register'})


@login_required
def member_edit(request, pk):
    """Edit member profile (FR-303)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('member_list')
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Member "{member.name}" updated.')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'library/member_form.html', {'form': form, 'action': 'Edit'})


@login_required
def member_delete(request, pk):
    """Delete / deactivate a member (FR-304)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('member_list')
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        name = member.name
        member.delete()
        messages.success(request, f'Member "{name}" removed.')
        return redirect('member_list')
    return render(request, 'library/confirm_delete.html', {'object': member, 'type': 'Member'})


@login_required
def member_detail(request, pk):
    """View member details with borrowing history."""
    member = get_object_or_404(Member, pk=pk)
    transactions = Transaction.objects.filter(member=member).select_related('book')
    fines = Fine.objects.filter(transaction__member=member)
    context = {
        'member': member,
        'transactions': transactions,
        'fines': fines,
        'active_count': member.active_issues_count(),
        'total_fines': fines.filter(paid=False).aggregate(s=Sum('amount'))['s'] or 0,
    }
    return render(request, 'library/member_detail.html', context)


# ─── Issue / Return Views ────────────────────────────────────

@login_required
def issue_list(request):
    """Display currently issued books (FR-407)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    active = Transaction.objects.filter(returned=False).select_related('book', 'member')
    return render(request, 'library/issue_list.html', {'issues': active})


@login_required
def issue_book(request):
    """Issue a book to a member (FR-401)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            book = form.cleaned_data['book']

            txn_id = _next_id('T', Transaction, 'transaction_id')
            issue_date = timezone.now().date()
            due_date = issue_date + timedelta(days=member.borrow_period_days)

            Transaction.objects.create(
                transaction_id=txn_id,
                book=book, member=member,
                issue_date=issue_date, due_date=due_date,
                returned=False, issued_by=request.user,
            )
            book.available_qty -= 1
            book.save()

            messages.success(
                request,
                f'"{book.title}" issued to {member.name}. '
                f'Due: {due_date.strftime("%d-%m-%Y")} ({member.borrow_period_days} days)'
            )
            return redirect('issue_list')
    else:
        form = IssueBookForm()
    return render(request, 'library/issue_form.html', {'form': form})


@login_required
def return_book(request, pk):
    """Process return (FR-403)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    txn = get_object_or_404(Transaction, pk=pk, returned=False)
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            txn.returned = True
            txn.return_date = return_date
            txn.save()

            txn.book.available_qty += 1
            txn.book.save()

            fine = txn.fine_amount()
            if fine > 0:
                fine_id = _next_id('F', Fine, 'fine_id')
                Fine.objects.create(
                    fine_id=fine_id,
                    transaction=txn,
                    amount=fine,
                    paid=False,
                )
                messages.warning(
                    request,
                    f'"{txn.book.title}" returned by {txn.member.name}. '
                    f'FINE: Rs.{fine} ({txn.days_overdue()} days overdue)'
                )
            else:
                messages.success(
                    request,
                    f'"{txn.book.title}" returned by {txn.member.name}. No fine.'
                )
            return redirect('issue_list')
    else:
        form = ReturnBookForm()
    return render(request, 'library/return_form.html', {'form': form, 'txn': txn})


@login_required
def transaction_history(request):
    """Complete transaction history (FR-407)."""
    txns = Transaction.objects.all().select_related('book', 'member')
    return render(request, 'library/transaction_history.html', {'transactions': txns})


# ─── Fine Views ───────────────────────────────────────────────

@login_required
def fine_list(request):
    """Display all fines (FR-502)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    status_filter = request.GET.get('status', '').strip()
    fines = Fine.objects.select_related('transaction__book', 'transaction__member').all()
    if status_filter == 'unpaid':
        fines = fines.filter(paid=False)
    elif status_filter == 'paid':
        fines = fines.filter(paid=True)

    total_unpaid = Fine.objects.filter(paid=False).aggregate(s=Sum('amount'))['s'] or 0
    total_collected = Fine.objects.filter(paid=True).aggregate(s=Sum('amount'))['s'] or 0

    context = {
        'fines': fines,
        'status_filter': status_filter,
        'total_unpaid': total_unpaid,
        'total_collected': total_collected,
    }
    return render(request, 'library/fine_list.html', context)


@login_required
def fine_pay(request, pk):
    """Record fine payment (FR-503)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('fine_list')
    fine = get_object_or_404(Fine, pk=pk, paid=False)
    if request.method == 'POST':
        form = PayFineForm(request.POST)
        if form.is_valid():
            fine.paid = True
            fine.paid_date = timezone.now().date()
            fine.collected_by = request.user
            fine.save()
            messages.success(
                request,
                f'Fine Rs.{fine.amount} collected from {fine.transaction.member.name}.'
            )
            return redirect('fine_list')
    else:
        form = PayFineForm()
    return render(request, 'library/fine_pay.html', {'form': form, 'fine': fine})


# ─── Report Views ─────────────────────────────────────────────

@login_required
def reports(request):
    """Reports dashboard (SRS §3.7)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    return render(request, 'library/reports.html')


@login_required
def report_overdue(request):
    """Overdue books report (FR-702)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    overdue = []
    for txn in Transaction.objects.filter(returned=False).select_related('book', 'member'):
        if txn.is_overdue():
            overdue.append(txn)
    return render(request, 'library/report_overdue.html', {'overdue': overdue})


@login_required
def report_popular(request):
    """Most popular books (FR-703)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    popular = Book.objects.annotate(
        issue_count=Count('transactions')
    ).order_by('-issue_count')[:10]
    return render(request, 'library/report_popular.html', {'popular': popular})


@login_required
def report_member_activity(request):
    """Member activity report (FR-704)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    members = Member.objects.annotate(
        total_issues=Count('transactions'),
        active_issues=Count('transactions', filter=Q(transactions__returned=False)),
    ).order_by('-total_issues')
    return render(request, 'library/report_members.html', {'members': members})


# ─── Category Views ───────────────────────────────────────────

@login_required
def category_list(request):
    """Manage book categories (FR-206)."""
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')
    cats = Category.objects.annotate(book_count=Count('books'))
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{form.cleaned_data["name"]}" added!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'library/category_list.html', {'categories': cats, 'form': form})


@login_required
def category_delete(request, pk):
    if not _is_staff(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('category_list')
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, f'Category deleted.')
        return redirect('category_list')
    return render(request, 'library/confirm_delete.html', {'object': cat, 'type': 'Category'})
