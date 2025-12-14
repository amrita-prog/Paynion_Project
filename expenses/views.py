from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ExpenseForm
from groups.models import Group


# --------------------------------------------------
# ADD EXPENSE FROM GROUP CARD (Group already selected)
# --------------------------------------------------
@login_required
def add_expense_in_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()
            form.save_m2m()

            messages.success(request, "Expense added successfully")
            return redirect("dashboard")
    else:
        form = ExpenseForm(group=group)

    return render(request, "expenses/add_expense.html", {
        "form": form,
        "group": group
    })


# --------------------------------------------------
# ADD EXPENSE FROM DASHBOARD (Group selection required)
# --------------------------------------------------
@login_required
def add_expense_direct(request):
    if request.method == "POST":
        group_id = request.POST.get("group")

        if not group_id:
            messages.error(request, "Please select a group")
            return redirect("add_expense")

        group = get_object_or_404(Group, id=group_id)

        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()
            form.save_m2m()

            messages.success(request, "Expense added successfully")
            return redirect("dashboard")
    else:
        form = ExpenseForm()

    return render(request, "expenses/add_expense.html", {
        "form": form,
        "group": None
    })
