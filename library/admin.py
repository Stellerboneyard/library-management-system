from django.contrib import admin
from .models import Book, Member, Transaction, Fine, Category, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'isbn', 'category', 'total_qty', 'available_qty')
    search_fields = ('book_id', 'title', 'author', 'isbn')
    list_filter = ('category',)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'name', 'member_type', 'department', 'phone', 'status')
    search_fields = ('member_id', 'name', 'department')
    list_filter = ('member_type', 'status')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'book', 'member', 'issue_date', 'due_date', 'returned', 'return_date')
    list_filter = ('returned',)
    search_fields = ('transaction_id',)


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('fine_id', 'transaction', 'amount', 'paid', 'paid_date')
    list_filter = ('paid',)
