from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from expenses.utils import calculate_group_balances
from .forms import GroupCreateForm
from .models import Group

User = get_user_model()


@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()
            return redirect("dashboard")
    else:
        form = GroupCreateForm()

    return render(request, "groups/create_group.html", {"form": form})


@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to edit this group.")
        return redirect("group_detail", group_id=group.id)

    if request.method == "POST":
        form = GroupCreateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("group_detail", group_id=group.id)
    else:
        form = GroupCreateForm(instance=group)

    return render(request, "groups/edit_group.html", {
        "form": form,
        "group": group
    })


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to delete this group.")
        return redirect("group_detail", group_id=group.id)

    if request.method == "POST":
        group.delete()
        return redirect("dashboard")

    return render(request, "groups/confirm_delete.html", {"group": group})


@login_required
def view_all_group(request):
    groups = Group.objects.filter(members=request.user)
    show_add_expense = request.GET.get("from") == "add_expense"

    return render(request, "groups/all_groups.html", {
        "groups": groups,
        "show_add_expense": show_add_expense
    })




@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    expenses = group.expenses.all().order_by("-created_at")

    # ✅ MUST be dictionary
    balances = calculate_group_balances(group)

    # 🔒 Debug safety check (temporary)
    if not isinstance(balances, dict):
        raise ValueError("balances must be a dictionary")

    return render(request, "groups/group_detail.html", {
        "group": group,
        "expenses": expenses,
        "balances": balances,
    })




@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to add members.")
        return redirect("group_detail", group_id=group.id)

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("group_detail", group_id=group.id)

        if user in group.members.all():
            messages.warning(request, "User already exists in this group.")
        else:
            group.members.add(user)
            messages.success(request, "Member added successfully.")

    return redirect("group_detail", group_id=group.id)


@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    user = get_object_or_404(User, id=user_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to remove members.")
        return redirect("group_detail", group_id=group.id)

    if user == group.created_by:
        messages.error(request, "Group creator cannot be removed.")
        return redirect("group_detail", group_id=group.id)

    group.members.remove(user)
    messages.success(request, "Member removed successfully.")

    return redirect("group_detail", group_id=group.id)
