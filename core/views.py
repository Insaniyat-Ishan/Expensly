from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Category
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CategoryForm
from django.views.generic import UpdateView, DeleteView
from django.views.generic import ListView, CreateView
from django.db.models import Q, Sum
from .forms import TransactionForm
from .models import Transaction, Category
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date
from .models import Budget
from .forms import BudgetForm
from .models import Budget
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum
from django.shortcuts import render
from .models import Category, Transaction

def home(request):
    """Landing page: show quick CTA for guests, summary cards for logged-in users."""
    if not request.user.is_authenticated:
        return render(request, "core/home.html", {"guest": True})

    user = request.user
    today = now().date()
    y, m = today.year, today.month

    month_qs = Transaction.objects.filter(owner=user, date__year=y, date__month=m)
    month_income = month_qs.filter(category__type="income").aggregate(s=Sum("amount"))["s"] or 0
    month_expense = month_qs.filter(category__type="expense").aggregate(s=Sum("amount"))["s"] or 0
    month_balance = month_income - month_expense

    # Last 3 recent transactions
    recent = (Transaction.objects
              .filter(owner=user)
              .select_related("category")
              .order_by("-date", "-id")[:3])

    ctx = {
        "guest": False,
        "month_income": month_income,
        "month_expense": month_expense,
        "month_balance": month_balance,
        "recent": recent,
        "year": y,
        "month": m,
    }
    return render(request, "core/home.html", ctx)

def signup(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already signed in.")
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile(request):
    user = request.user
    today = now().date()
    y, m = today.year, today.month

    # Counts
    category_count = Category.objects.filter(owner=user).count()
    txn_count = Transaction.objects.filter(owner=user).count()

    # This month totals
    month_qs = Transaction.objects.filter(owner=user, date__year=y, date__month=m)
    month_income = month_qs.filter(category__type="income").aggregate(s=Sum("amount"))["s"] or 0
    month_expense = month_qs.filter(category__type="expense").aggregate(s=Sum("amount"))["s"] or 0
    month_balance = month_income - month_expense

    # Recent transactions
    recent = (Transaction.objects
              .filter(owner=user)
              .select_related("category")
              .order_by("-date", "-id")[:5])

    ctx = {
        "category_count": category_count,
        "txn_count": txn_count,
        "month_income": month_income,
        "month_expense": month_expense,
        "month_balance": month_balance,
        "recent": recent,
        "year": y,
        "month": m,
    }
    return render(request, "core/profile.html", ctx)
class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    template_name = "core/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        qs = Category.objects.filter(owner=self.request.user)
        q = self.request.GET.get("q", "")
        t = self.request.GET.get("type", "")
        if q:
            qs = qs.filter(name__icontains=q)
        if t in ("income", "expense"):
            qs = qs.filter(type=t)
        return qs.order_by("name")



class CategoryCreate(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "core/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)

class CategoryUpdate(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "core/category_form.html"   # reuse the same form template
    success_url = reverse_lazy("category_list")

    def get_queryset(self):
        # ensure users can edit only their own categories
        return Category.objects.filter(owner=self.request.user)
    
class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "core/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")

    def get_queryset(self):
        # ensure users can delete only their own categories
        return Category.objects.filter(owner=self.request.user)

class TransactionList(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "core/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Transaction.objects.filter(owner=user).select_related("category")
        q = self.request.GET.get("q", "")
        t = self.request.GET.get("type", "")
        cat = self.request.GET.get("category", "")
        dfrom = self.request.GET.get("from", "")
        dto = self.request.GET.get("to", "")

        if q:
            qs = qs.filter(Q(note__icontains=q) | Q(category__name__icontains=q))
        if t in ("income", "expense"):
            qs = qs.filter(category__type=t)
        if cat:
            qs = qs.filter(category__name=cat)
        if dfrom:
            qs = qs.filter(date__gte=dfrom)
        if dto:
            qs = qs.filter(date__lte=dto)
        return qs.order_by("-date", "-id")

def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["categories"] = Category.objects.filter(owner=user).order_by("name")

        # existing totals
        base_qs = self.get_queryset()
        ctx["total_income"] = base_qs.filter(category__type="income").aggregate(Sum("amount"))["amount__sum"] or 0
        ctx["total_expense"] = base_qs.filter(category__type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
        ctx["balance"] = ctx["total_income"] - ctx["total_expense"]

        # 👇 NEW: budget progress for current month
        today = now().date()
        y, m = today.year, today.month

        # Spend this month per expense category
        spent_rows = (Transaction.objects
                      .filter(owner=user, date__year=y, date__month=m, category__type="expense")
                      .values("category__id", "category__name")
                      .annotate(spent=Sum("amount"))
                      .order_by())

        spent_map = {r["category__id"]: float(r["spent"]) for r in spent_rows}

        # Budgets this month
        budgets = (Budget.objects
                   .filter(owner=user, year=y, month=m)
                   .select_related("category")
                   .order_by("category__name"))

        progress = []
        for b in budgets:
            spent = spent_map.get(b.category_id, 0.0)
            limit = float(b.limit)
            pct = 0 if limit == 0 else min(100, round(spent / limit * 100))
            over = spent > limit
            progress.append({
                "category": b.category.name,
                "limit": limit,
                "spent": spent,
                "pct": pct,
                "over": over,
            })

        ctx["budget_progress"] = progress  # 👈 expose to template
        ctx["budget_year"] = y
        ctx["budget_month"] = m
        return ctx

class TransactionCreate(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "core/transaction_form.html"
    success_url = reverse_lazy("transaction_list")

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["category"].queryset = Category.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)
    

class TransactionUpdate(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "core/transaction_form.html"
    success_url = reverse_lazy("transaction_list")

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["category"].queryset = Category.objects.filter(owner=self.request.user)
        return form


class TransactionDelete(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "core/transaction_confirm_delete.html"
    success_url = reverse_lazy("transaction_list")

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user)


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")

@login_required
def summary_api(request):
    user = request.user
    today = now().date()
    first_of_month = today.replace(day=1)

    # Current month: totals by category (for pie)
    qs_month = (Transaction.objects
                .filter(owner=user, date__gte=first_of_month, date__lte=today)
                .select_related("category"))
    cat_totals = (qs_month.values("category__name", "category__type")
                          .annotate(total=Sum("amount"))
                          .order_by())

    # Helper: 11 months ago (start of month)
    def months_ago_start(dt: date, n: int) -> date:
        y, m = dt.year, dt.month - n
        while m <= 0:
            m += 12
            y -= 1
        return date(y, m, 1)

    start_12 = months_ago_start(first_of_month, 11)

    # Last 12 months: totals per month & type (for line chart)
    series = (Transaction.objects
              .filter(owner=user, date__gte=start_12, date__lte=today)
              .annotate(month=TruncMonth("date"))
              .values("month", "category__type")
              .annotate(total=Sum("amount"))
              .order_by("month", "category__type"))

    data = {
        "categories": [
            {
                "name": r["category__name"],
                "type": r["category__type"],
                "total": float(r["total"]),
            } for r in cat_totals
        ],
        "monthly": [
            {
                "month": r["month"].strftime("%Y-%m"),
                "type": r["category__type"],
                "total": float(r["total"]),
            } for r in series
        ],
    }
    return JsonResponse(data)




class BudgetList(LoginRequiredMixin, ListView):
    model = Budget
    template_name = "core/budget_list.html"
    context_object_name = "budgets"

    def get_queryset(self):
        qs = Budget.objects.filter(owner=self.request.user).select_related("category")
        # optional filters
        y = self.request.GET.get("year", "")
        m = self.request.GET.get("month", "")
        if y.isdigit():
            qs = qs.filter(year=int(y))
        if m.isdigit():
            qs = qs.filter(month=int(m))
        return qs.order_by("-year", "-month", "category__name")

class BudgetCreate(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "core/budget_form.html"
    success_url = reverse_lazy("budget_list")

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        # limit categories to the current user's categories (usually expense, but allow both)
        form.fields["category"].queryset = self.request.user.categories.all().order_by("name")
        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        return super().form_valid(form)


from django.views.decorators.http import require_GET
from .models import Budget

@login_required
@require_GET
def budget_summary_api(request):
    user = request.user
    today = now().date()
    y, m = today.year, today.month

    # Spent this month per EXPENSE category
    spent_rows = (Transaction.objects
                  .filter(owner=user, date__year=y, date__month=m, category__type="expense")
                  .values("category__id", "category__name")
                  .annotate(spent=Sum("amount"))
                  .order_by())
    spent_map = {r["category__id"]: float(r["spent"]) for r in spent_rows}

    # Budgets this month
    budgets = (Budget.objects
               .filter(owner=user, year=y, month=m)
               .select_related("category")
               .order_by("category__name"))

    progress = []
    for b in budgets:
        spent = spent_map.get(b.category_id, 0.0)
        limit = float(b.limit)
        pct = 0 if limit == 0 else min(100, round(spent / limit * 100))
        over = spent > limit
        progress.append({
            "category": b.category.name,
            "limit": limit,
            "spent": spent,
            "pct": pct,
            "over": over,
        })

    return JsonResponse({
        "year": y,
        "month": m,
        "items": progress,
    })
