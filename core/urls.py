# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("accounts/signup/", views.signup, name="signup"),
    path("categories/", views.CategoryList.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreate.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdate.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDelete.as_view(), name="category_delete"),
    path("transactions/", views.TransactionList.as_view(), name="transaction_list"),
    path("transactions/new/", views.TransactionCreate.as_view(), name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.TransactionUpdate.as_view(), name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.TransactionDelete.as_view(), name="transaction_delete"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/summary/", views.summary_api, name="summary_api"),
    path("budgets/", views.BudgetList.as_view(), name="budget_list"),
    path("budgets/new/", views.BudgetCreate.as_view(), name="budget_create"),
    path("api/budgets/", views.budget_summary_api, name="budget_summary_api"),



    # (If you've added CRUD views already, keep these too)
    # path("categories/", views.CategoryList.as_view(), name="category_list"),
    # path("categories/new/", views.CategoryCreate.as_view(), name="category_create"),
    # path("categories/<int:pk>/edit/", views.CategoryUpdate.as_view(), name="category_update"),
    # path("categories/<int:pk>/delete/", views.CategoryDelete.as_view(), name="category_delete"),

    # path("transactions/", views.TransactionList.as_view(), name="transaction_list"),
    # path("transactions/new/", views.TransactionCreate.as_view(), name="transaction_create"),
    # path("transactions/<int:pk>/edit/", views.TransactionUpdate.as_view(), name="transaction_update"),
    # path("transactions/<int:pk>/delete/", views.TransactionDelete.as_view(), name="transaction_delete"),
]
