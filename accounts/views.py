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
from accounts.models import Notification

from django.views.decorators.http import require_POST
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



# 


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # 🔔 FETCH UNREAD NOTIFICATION (IMPORTANT)
    notification = (
        Notification.objects
        .filter(user=user, is_read=False)
        .first()
    )

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
    total_weeks = max(1, account_age_days // 7 + 1)

    #  DROPDOWN OPTIONS 
    week_options = [{"value": 1, "label": "This Week"}]

    if total_weeks >= 2:
        week_options.append({"value": 2, "label": "Last Week"})

    for i in range(3, total_weeks + 1):
        week_options.append({"value": i, "label": f"Last {i} Weeks"})

    week_options.append({"value": "all", "label": "All Time"})

    #  SELECTED RANGE 
    selected = request.GET.get("weeks", "1")

    if selected == "all":
        start_date = None
    else:
        start_date = today - timedelta(days=int(selected) * 7)

    #  PAID BY ME 
    paid_qs = Expense.objects.filter(paid_by=user)
    if start_date:
        paid_qs = paid_qs.filter(created_at__date__gte=start_date)

    paid_data = (
        paid_qs
        .values("created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("created_at__date")
    )

    #  I NEED TO PAY 
    need_to_pay_qs = ExpenseSplit.objects.filter(user=user).exclude(expense__paid_by=user)
    if start_date:
        need_to_pay_qs = need_to_pay_qs.filter(expense__created_at__date__gte=start_date)

    need_to_pay_data = (
        need_to_pay_qs
        .values("expense__created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("expense__created_at__date")
    )

    #  FORMAT DATA 
    def format_data(qs, date_key):
        labels, values = [], []
        for item in qs:
            labels.append(item[date_key].strftime("%d %b"))
            values.append(float(item["total"]))
        return labels, values

    paid_labels, paid_values = format_data(paid_data, "created_at__date")
    need_labels, need_values = format_data(need_to_pay_data, "expense__created_at__date")

    context = {
        "notification": notification,   # ✅ PASS TO TEMPLATE
        "total_groups": total_groups,
        "total_expenses": total_expenses,
        "recent_expenses": recent_expenses,
        "week_options": week_options,
        "chart": {
            "labels": paid_labels,
            "paid": paid_values,
            "need_to_pay": need_values,
        }
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

            # ✅ ADD SUCCESS MESSAGE (THIS TRIGGERS TOAST)
            messages.success(request, "Profile updated successfully!")

            return redirect("accounts:edit_profile")  # redirect back to same page

    else:
        form = EditProfileForm(instance=user)

    return render(request, "accounts/edit_profile.html", {
        "form": form
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({"status": "ok"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error"}, status=404)