from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

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

            # 🔹 selected users from checkbox
            users = form.cleaned_data["split_between"]

            # 🔹 safety: delete old splits
            expense.splits.all().delete()

            try:
                if expense.split_type == "equal":
                    handle_equal_split(expense, users)

                elif expense.split_type == "percentage":
                    handle_percentage_split(expense, users, request.POST)

                elif expense.split_type == "custom":
                    handle_custom_split(expense, users, request.POST)

            except ValueError as e:
                messages.error(request, str(e))
                expense.delete()
                return redirect(request.path)

            messages.success(request, "Expense added successfully")
            return redirect("group_detail", group_id=group.id)

    else:
        form = ExpenseForm(group=group)

    return render(request, "expenses/add_expense.html", {
        "form": form,
        "group": group
    })
