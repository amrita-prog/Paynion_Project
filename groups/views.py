from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import GroupCreateForm
from .models import Group


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user  # auto set creator
            group.save()
            form.save_m2m()  # for saving members 

            return redirect("dashboard")
    else:
        form = GroupCreateForm()

    return render(request, "groups/create_group.html", {"form": form})


@login_required
def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect("dashboard")
    return render(request, "groups/confirm_delete.html", {"group": group})


@login_required
def view_all_group(request):
    groups = Group.objects.filter(members=request.user)

    # flag to decide AddExpense button dikhana hai ya nahi
    show_add_expense = request.GET.get("from") == "add_expense"

    return render(request, "groups/all_groups.html", {
        "groups": groups,
        "show_add_expense": show_add_expense
    })


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    expenses = group.expenses.all()

    return render(request, "groups/group_detail.html", {
        "group": group,
        "expenses": expenses
    })
