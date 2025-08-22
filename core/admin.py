from django.contrib import admin
from .models import Category, Transaction
from .models import Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "owner", "created_at")
    list_filter = ("type",)
    search_fields = ("name", "owner__username")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "amount", "owner", "created_at")
    list_filter = ("category__type", "date")
    search_fields = ("note", "owner__username", "category__name")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("category", "year", "month", "limit", "owner", "created_at")
    list_filter = ("year", "month", "category__type")
    search_fields = ("category__name", "owner__username")
