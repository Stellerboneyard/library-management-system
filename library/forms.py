"""
Forms for Library Management System.
Handles Book, Member, Transaction, Fine, and authentication forms.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Book, Member, Transaction, Fine, Category, UserProfile


# ─── Auth Forms ───────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    """Custom login form with styled fields."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username or Email', 'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password',
    }))


class RegisterForm(forms.Form):
    """Registration form for new users (FR-101)."""
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Username',
    }))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'First Name',
    }))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input', 'placeholder': 'Last Name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email Address',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password (min 6 chars)',
    }))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-input',
    }))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters.")
        return password


# ─── Book Forms ───────────────────────────────────────────────

class BookForm(forms.ModelForm):
    """Form for adding / editing a book (FR-201, FR-202)."""
    class Meta:
        model = Book
        fields = ['book_id', 'title', 'author', 'isbn', 'publisher', 'edition', 'category', 'total_qty']
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. B001'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Author Name(s)'}),
            'isbn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '978-X-XXXX-XXXX-X'}),
            'publisher': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Publisher'}),
            'edition': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 3rd Edition'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'total_qty': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'placeholder': '1'}),
        }

    def save(self, commit=True):
        book = super().save(commit=False)
        if not book.pk:
            book.available_qty = book.total_qty
        if commit:
            book.save()
        return book


# ─── Member Forms ─────────────────────────────────────────────

class MemberForm(forms.ModelForm):
    """Form for registering / editing a member (FR-301, FR-303)."""
    class Meta:
        model = Member
        fields = ['member_id', 'name', 'member_type', 'department', 'phone', 'email', 'status']
        widgets = {
            'member_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. LIB-2026-001'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'member_type': forms.Select(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSE'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '9876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@example.com'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


# ─── Issue / Return Forms ────────────────────────────────────

class IssueBookForm(forms.Form):
    """Form for issuing a book to a member (FR-401)."""
    member = forms.ModelChoiceField(
        queryset=Member.objects.filter(status='active'),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="— Select Member —"
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_qty__gt=0),
        widget=forms.Select(attrs={'class': 'form-input'}),
        empty_label="— Select Available Book —"
    )

    def clean(self):
        cleaned = super().clean()
        member = cleaned.get('member')
        book = cleaned.get('book')
        if member and book:
            can, reason = member.can_borrow()
            if not can:
                raise forms.ValidationError(reason)
            # Check duplicate active issue
            if Transaction.objects.filter(member=member, book=book, returned=False).exists():
                raise forms.ValidationError(
                    f"'{member.name}' already has an active issue for '{book.title}'."
                )
        return cleaned


class ReturnBookForm(forms.Form):
    """Form for processing a book return (FR-403)."""
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        initial=timezone.now().date,
    )


class PayFineForm(forms.Form):
    """Form for recording fine payment (FR-503)."""
    confirm = forms.BooleanField(
        required=True,
        label="I confirm the fine has been collected.",
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
    )


# ─── Category Form ───────────────────────────────────────────

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Category Name'}),
        }
