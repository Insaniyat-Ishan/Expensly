from django import forms
from .models import Category, Transaction
from .models import Budget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type"]

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["category", "amount", "note", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["category", "year", "month", "limit"]
        widgets = {
            "year": forms.NumberInput(attrs={"min": 2000, "step": 1}),
            "month": forms.NumberInput(attrs={"min": 1, "max": 12, "step": 1}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["category", "amount", "note", "date", "receipt"]  # 👈 added
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
