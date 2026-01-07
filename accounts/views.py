from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from .forms import SignUpForm, EditProfileForm
from django.contrib.auth import login, logout, authenticate 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from groups.models import Group, GroupInvite
from expenses.models import Expense, ExpenseSplit
from django.db.models import Sum
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
import os

User = get_user_model()


def signup_view(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please log in.")
            login_url = reverse('accounts:login')
            if next_url:
                return redirect(f"{login_url}?next={next_url}")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form, 'next': next_url})



def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")

            # MAIN FIX
            if next_url:
                return redirect(next_url)

            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html", {"next": next_url})



@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    #  INVITE REDIRECT 
    pending_invites = GroupInvite.objects.filter(
        email=user.email,
        is_accepted=False
    )

    if pending_invites.exists():
        invite = pending_invites.first()
        return redirect("groups:accept_invite", token=invite.token)

    #  SUMMARY CARDS 
    total_groups = Group.objects.filter(members=user).count()
    total_expenses = Expense.objects.filter(paid_by=user).count()

    recent_expenses = (
        Expense.objects
        .filter(paid_by=user)
        .order_by('-created_at')[:5]
    )

    #  ACCOUNT AGE 
    account_age_days = (today - user.date_joined.date()).days
    show_last_week = account_age_days >= 7

    #  DATE RANGES 
    start_this_week = today - timedelta(days=today.weekday())
    start_last_week = start_this_week - timedelta(days=7)
    end_last_week = start_this_week - timedelta(days=1)

    #  THIS WEEK DATA 
    this_week_paid = (
        Expense.objects
        .filter(paid_by=user, created_at__date__gte=start_this_week)
        .values('created_at__date')
        .annotate(total=Sum('amount'))
    )

    this_week_received = (
        ExpenseSplit.objects
        .filter(user=user, expense__created_at__date__gte=start_this_week)
        .exclude(expense__paid_by=user)
        .values('expense__created_at__date')
        .annotate(total=Sum('amount'))
    )

    def format_data(qs):
        labels, values = [], []
        for item in qs:
            labels.append(item[list(item.keys())[0]].strftime("%a"))
            values.append(float(item["total"]))
        return labels, values

    tw_paid_labels, tw_paid_values = format_data(this_week_paid)
    tw_recv_labels, tw_recv_values = format_data(this_week_received)

    context = {
        "total_groups": total_groups,
        "total_expenses": total_expenses,
        "recent_expenses": recent_expenses,
        "balance": 0,  # (future calculation)
        "this_week": {
            "labels": tw_paid_labels,
            "paid": tw_paid_values,
            "received": tw_recv_values,
        },
        "show_last_week": show_last_week,
    }

    #  LAST WEEK (ONLY IF VALID) 
    if show_last_week:
        last_week_paid = (
            Expense.objects
            .filter(
                paid_by=user,
                created_at__date__range=(start_last_week, end_last_week)
            )
            .values('created_at__date')
            .annotate(total=Sum('amount'))
        )

        last_week_received = (
            ExpenseSplit.objects
            .filter(
                user=user,
                expense__created_at__date__range=(start_last_week, end_last_week)
            )
            .exclude(expense__paid_by=user)
            .values('expense__created_at__date')
            .annotate(total=Sum('amount'))
        )

        lw_paid_labels, lw_paid_values = format_data(last_week_paid)
        lw_recv_labels, lw_recv_values = format_data(last_week_received)

        context["last_week"] = {
            "labels": lw_paid_labels,
            "paid": lw_paid_values,
            "received": lw_recv_values,
        }

    return render(request, "accounts/dashboard.html", context)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("accounts:login")




@login_required
def profile_view(request):
    user = request.user

    groups = Group.objects.filter(members=user)

    # Total Paid by Me
    total_paid_by_me = Expense.objects.filter(
        paid_by=user
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total I Need to Pay
    total_need_to_pay = ExpenseSplit.objects.filter(
        user=user
    ).exclude(
        expense__paid_by=user
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total I Will Get Back
    total_get_back = ExpenseSplit.objects.filter(
        expense__paid_by=user
    ).exclude(
        user=user
    ).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        "user": user,
        "groups":groups,
        "total_paid_by_me": total_paid_by_me,
        "total_need_to_pay": total_need_to_pay,
        "total_get_back": total_get_back,
    }

    return render(request, "accounts/profile.html", context)



@login_required
def my_paid_expenses(request):
    user = request.user
    expenses = Expense.objects.filter(paid_by=request.user).select_related("group")
    return render(request, 'accounts/my_paid_expenses.html', {'expenses': expenses})



@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():

            # REMOVE PROFILE IMAGE
            if request.POST.get("remove_image"):
                if user.profile_image and user.profile_image.name != "default_profile.jpg":
                    image_path = os.path.join(settings.MEDIA_ROOT, user.profile_image.name)
                    if os.path.exists(image_path):
                        os.remove(image_path)

                user.profile_image = "default_profile.jpg"
                user.save()

            else:
                form.save()

            return redirect("accounts:profile")

    else:
        form = EditProfileForm(instance=user)

    return render(request, "accounts/edit_profile.html", {
        "form": form
    })