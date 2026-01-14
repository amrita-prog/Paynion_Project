from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from expenses.utils import calculate_group_balances, calculate_settlements
from .forms import GroupCreateForm
from django.conf import settings
from django.core.mail import send_mail
from .models import Group, GroupInvite
from django.http import HttpResponse
from django.urls import reverse
from django.utils.http import urlencode

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
            return redirect("accounts:dashboard")
    else:
        form = GroupCreateForm()

    return render(request, "groups/create_group.html", {"form": form})


@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to edit this group.")
        return redirect("groups:group_detail", group_id=group.id)

    if request.method == "POST":
        form = GroupCreateForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("groups:group_detail", group_id=group.id)
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
        return redirect("groups:group_detail", group_id=group.id)

    if request.method == "POST":
        group.delete()
        return redirect("accounts:dashboard")

    return render(request, "groups/confirm_delete.html", {"group": group})


@login_required
def view_all_group(request):
    groups = Group.objects.filter(members=request.user)
    show_add_expense = request.GET.get("from") == "add_expense"

    return render(request, "groups/all_groups.html", {
        "groups": groups,
        "show_add_expense": show_add_expense
    })





# @login_required
# def group_detail(request, group_id):
#     group = get_object_or_404(Group, id=group_id)

#     expenses = group.expenses.all().order_by("-created_at")
#     balances = calculate_group_balances(group)

#     settlements = Settlement.objects.filter(
#         group=group,
#         status__in=["PENDING", "PAID_REQUESTED"]
#     )

#     is_admin = request.user == group.created_by

#     return render(request, "groups/group_detail.html", {
#         "group": group,
#         "expenses": expenses,
#         "balances": balances,
#         "settlements": settlements,
#         "is_admin": is_admin,
#     })

from payments.models import Settlement
from django.db import transaction

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    expenses = group.expenses.all().order_by("-created_at")
    balances = calculate_group_balances(group)

    # 1️⃣ calculate settlements (memory)
    calculated_settlements = calculate_settlements(balances)

    # 2️⃣ persist settlements into DB
    with transaction.atomic():
        for s in calculated_settlements:
            Settlement.objects.get_or_create(
                group=group,
                payer=s["from"],
                receiver=s["to"],
                defaults={
                    "amount": s["amount"],
                    "status": "PENDING"
                }
            )

    # 3️⃣ fetch active settlements from DB
    settlements = Settlement.objects.filter(
        group=group,
        status__in=["PENDING", "PAID_REQUESTED"]
    )

    is_admin = request.user == group.created_by

    return render(request, "groups/group_detail.html", {
        "group": group,
        "expenses": expenses,
        "balances": balances,
        "settlements": settlements,
        "is_admin": is_admin,
    })




@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to add members.")
        return redirect("groups:group_detail", group_id=group.id)

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("groups:group_detail", group_id=group.id)

        if user in group.members.all():
            messages.warning(request, "User already exists in this group.")
        else:
            group.members.add(user)
            messages.success(request, "Member added successfully.")

    return redirect("groups:group_detail", group_id=group.id)


@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    user = get_object_or_404(User, id=user_id)

    if request.user != group.created_by:
        messages.error(request, "You are not allowed to remove members.")
        return redirect("groups:group_detail", group_id=group.id)

    if user == group.created_by:
        messages.error(request, "Group creator cannot be removed.")
        return redirect("groups:group_detail", group_id=group.id)

    group.members.remove(user)
    messages.success(request, "Member removed successfully.")

    return redirect("groups:group_detail", group_id=group.id)




@login_required
def send_group_invite(request, group_id):
    if request.method == "POST":
        email = request.POST.get("email")
        group = get_object_or_404(Group, id=group_id)
        invite = GroupInvite.objects.create(email=email,group=group,invited_by=request.user)

        invite_link = f"http://127.0.0.1:8000/groups/invite/accept/{invite.token}/"

        send_mail(
            subject=f"Invite to join {group.title}",
            message=f"""
You have been invited to join the group "{group.title}"

Click below to accept the invite:
{invite_link}

If you are not logged in, you will be asked to login or signup first.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )

        return redirect("groups:group_detail", group_id=group.id)


@login_required
def accept_group_invite(request, token):
    invite = get_object_or_404(GroupInvite, token=token, is_accepted=False)

    if invite.email != request.user.email:
        messages.error(request, "This invitation is not for your email address.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        if request.POST.get("action") == "accept":
            invite.group.members.add(request.user)
            invite.is_accepted = True
            invite.save()
            messages.success(request, "You have successfully joined the group!")
            return redirect("groups:group_detail", group_id=invite.group.id)

        else:
            invite.delete()
            messages.info(request, "Invitation rejected.")
            return redirect("accounts:dashboard")

    return render(request, "groups/accept_invite.html", {"invite": invite})
