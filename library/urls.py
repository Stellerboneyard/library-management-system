"""URL configuration for the library app."""

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Issues / Returns
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/new/', views.issue_book, name='issue_book'),
    path('issues/<int:pk>/return/', views.return_book, name='return_book'),
    path('issues/history/', views.transaction_history, name='transaction_history'),

    # Fines
    path('fines/', views.fine_list, name='fine_list'),
    path('fines/<int:pk>/pay/', views.fine_pay, name='fine_pay'),

    # Reports
    path('reports/', views.reports, name='reports'),
    path('reports/overdue/', views.report_overdue, name='report_overdue'),
    path('reports/popular/', views.report_popular, name='report_popular'),
    path('reports/members/', views.report_member_activity, name='report_members'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
