from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Expense, ExpenseSplit
from .forms import ExpenseForm
from .services import (
    handle_equal_split,
    handle_percentage_split,
    handle_custom_split
)
from groups.models import Group

User = get_user_model()


@login_required
def add_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, group=group)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()

            users = form.cleaned_data["split_between"]
            expense.splits.all().delete()

            if expense.split_type == "equal":
                handle_equal_split(expense, users)
            elif expense.split_type == "percentage":
                handle_percentage_split(expense, users, request.POST)
            elif expense.split_type == "custom":
                handle_custom_split(expense, users, request.POST)

            messages.success(request, "Expense added successfully")
            return redirect("groups:group_detail", group.id)

    else:
        form = ExpenseForm(group=group)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "group": group
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id = expense_id)

    if request.user != expense.paid_by:
        messages.error(request, "You do not have permission to delete this expense.")
        return redirect("groups:group_detail", group_id=expense.group.id)
    
    expense.delete()

    messages.success(request, "Expense deleted successfully.")
    return redirect("groups:group_detail", group_id=expense.group.id)


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    group = expense.group

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense, group=group)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.save()

            expense.splits.all().delete()
            users = form.cleaned_data["split_between"]

            if expense.split_type == "equal":
                handle_equal_split(expense, users)
            elif expense.split_type == "percentage":
                handle_percentage_split(expense, users, request.POST)
            elif expense.split_type == "custom":
                handle_custom_split(expense, users, request.POST)

            messages.success(request, "Expense updated successfully")
            return redirect("groups:group_detail", group.id)

    else:
        form = ExpenseForm(instance=expense, group=group)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "expense": expense,
        "group": group,
    })
