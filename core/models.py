from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


TYPE_CHOICES = (
    ("income", "Income"),
    ("expense", "Expense"),
)

class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "name", "type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    receipt = models.ImageField(upload_to="receipts/", blank=True, null=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.date} • {self.category} • {self.amount}"



class Budget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    limit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "category", "year", "month")
        ordering = ["-year", "-month", "category__name"]

    def __str__(self):
        return f"{self.category.name} • {self.year}-{self.month:02d}: {self.limit}"
