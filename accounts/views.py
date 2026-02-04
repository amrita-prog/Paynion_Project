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
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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



def format_data(qs, date_key):
        labels, values = [], []
        for item in qs:
            labels.append(item[date_key].strftime("%d %b"))
            values.append(float(item["total"]))
        return labels, values


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    #  FETCH UNREAD NOTIFICATION (IMPORTANT)
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
    groups = Group.objects.filter(members=user).order_by('-created_at')

    recent_expenses = (
        Expense.objects
        .filter(paid_by=user)
        .order_by('-created_at')
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


    #  I WILL GET BACK (OTHERS OWE ME)
    will_get_back_qs = (
        ExpenseSplit.objects
        .filter(expense__paid_by=user)
        .exclude(user=user)
    )

    if start_date:
        will_get_back_qs = will_get_back_qs.filter(
            expense__created_at__date__gte=start_date
        )

    will_get_back_data = (
        will_get_back_qs
        .values("expense__created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("expense__created_at__date")
    )

    getback_labels, getback_values = format_data(
        will_get_back_data,
        "expense__created_at__date"
    )


    #  FORMAT DATA FOR CHART

    paid_labels, paid_values = format_data(paid_data, "created_at__date")
    need_labels, need_values = format_data(need_to_pay_data, "expense__created_at__date")

    # WEEKLY INCOME/OUTCOME DATA (Last 4 weeks)
    four_weeks_ago = today - timedelta(days=28)
    
    weekly_income_qs = (
        Expense.objects
        .filter(paid_by=user, created_at__date__gte=four_weeks_ago)
        .values('created_at__date')
        .annotate(total=Sum('amount'))
        .order_by('created_at__date')
    )
    
    weekly_outcome_qs = (
        ExpenseSplit.objects
        .filter(user=user, expense__created_at__date__gte=four_weeks_ago)
        .exclude(expense__paid_by=user)
        .values('expense__created_at__date')
        .annotate(total=Sum('amount'))
        .order_by('expense__created_at__date')
    )
    
    # Build weekly data for last 4 weeks
    week_labels = []
    income_by_week = [0, 0, 0, 0]
    outcome_by_week = [0, 0, 0, 0]
    
    for week_num in range(3, -1, -1):
        week_start = today - timedelta(days=week_num*7)
        week_end = week_start + timedelta(days=6)
        week_label = f"Week {4-week_num}"
        week_labels.append(week_label)
        
        # Calculate income for this week
        week_income = 0
        for item in weekly_income_qs:
            item_date = item['created_at__date']
            if week_start <= item_date <= week_end:
                week_income += float(item['total']) if item['total'] else 0
        income_by_week[3-week_num] = week_income
        
        # Calculate outcome for this week
        week_outcome = 0
        for item in weekly_outcome_qs:
            item_date = item['expense__created_at__date']
            if week_start <= item_date <= week_end:
                week_outcome += float(item['total']) if item['total'] else 0
        outcome_by_week[3-week_num] = week_outcome

    # Calculate totals for summary
    total_paid = sum(float(val) if val else 0 for val in paid_values)
    total_need_to_pay = sum(float(val) if val else 0 for val in need_values)
    total_will_get_back = sum(float(val) if val else 0 for val in getback_values)

    # ============================================
    # NEW CHART DATA - "YOU OWE VS YOU ARE OWED"
    # ============================================
    
    # Get period parameter (default: 4weeks)
    chart_period = request.GET.get('chart_period', '4weeks')
    
    # Determine date range and labels based on period
    if chart_period == '4days':
        num_periods = 4
        chart_start_date = today - timedelta(days=3)
        period_labels = []
        for i in range(4):
            day = today - timedelta(days=(3-i))
            period_labels.append(day.strftime("%a"))  # Mon, Tue, Wed, Thu
            
    elif chart_period == '4months':
        num_periods = 4
        chart_start_date = today - timedelta(days=120)  # ~4 months
        period_labels = []
        for i in range(4):
            month_date = today - timedelta(days=(3-i)*30)
            period_labels.append(month_date.strftime("%b"))  # Nov, Dec, Jan, Feb
            
    else:  # default: 4weeks
        num_periods = 4
        chart_start_date = today - timedelta(days=27)  # 4 weeks = 28 days, so 27 days back
        period_labels = []
        for i in range(4):
            week_start = today - timedelta(days=(3-i)*7)
            week_end = week_start + timedelta(days=6) if i < 3 else today
            period_labels.append(f"{week_start.strftime('%d %b')}")  # "01 Jan", "08 Jan", etc.
    
    # Fetch "You Owe" data (money you need to pay to others)
    you_owe_qs = (
        ExpenseSplit.objects
        .filter(user=user, expense__created_at__date__gte=chart_start_date)
        .exclude(expense__paid_by=user)
        .values('expense__created_at__date')
        .annotate(total=Sum('amount'))
        .order_by('expense__created_at__date')
    )
    
    # Fetch "You Are Owed" data (money others owe you)
    you_are_owed_qs = (
        ExpenseSplit.objects
        .filter(expense__paid_by=user, expense__created_at__date__gte=chart_start_date)
        .exclude(user=user)
        .values('expense__created_at__date')
        .annotate(total=Sum('amount'))
        .order_by('expense__created_at__date')
    )
    
    # Initialize data arrays
    you_owe_data = [0] * num_periods
    you_are_owed_data = [0] * num_periods
    
    # Bucket data into periods with CORRECT date calculations
    for period_idx in range(num_periods):
        if chart_period == '4days':
            # Each period is exactly 1 day
            period_date = today - timedelta(days=(3 - period_idx))
            
            # Sum "You Owe" for this day
            for item in you_owe_qs:
                if item['expense__created_at__date'] == period_date:
                    you_owe_data[period_idx] += float(item['total']) if item['total'] else 0
            
            # Sum "You Are Owed" for this day
            for item in you_are_owed_qs:
                if item['expense__created_at__date'] == period_date:
                    you_are_owed_data[period_idx] += float(item['total']) if item['total'] else 0
                    
        elif chart_period == '4months':
            # Each period is approximately 30 days
            period_end = today - timedelta(days=(3 - period_idx) * 30)
            period_start = period_end - timedelta(days=29)
            
            # Sum "You Owe" for this month period
            for item in you_owe_qs:
                item_date = item['expense__created_at__date']
                if period_start <= item_date <= period_end:
                    you_owe_data[period_idx] += float(item['total']) if item['total'] else 0
            
            # Sum "You Are Owed" for this month period
            for item in you_are_owed_qs:
                item_date = item['expense__created_at__date']
                if period_start <= item_date <= period_end:
                    you_are_owed_data[period_idx] += float(item['total']) if item['total'] else 0
                    
        else:  # 4weeks
            # Each period is 7 days
            period_end = today - timedelta(days=(3 - period_idx) * 7)
            period_start = period_end - timedelta(days=6)
            
            # Sum "You Owe" for this week
            for item in you_owe_qs:
                item_date = item['expense__created_at__date']
                if period_start <= item_date <= period_end:
                    you_owe_data[period_idx] += float(item['total']) if item['total'] else 0
            
            # Sum "You Are Owed" for this week
            for item in you_are_owed_qs:
                item_date = item['expense__created_at__date']
                if period_start <= item_date <= period_end:
                    you_are_owed_data[period_idx] += float(item['total']) if item['total'] else 0
    
    # ============================================
    # CATEGORY BREAKDOWN - LAST 30 DAYS
    # ============================================
    
    thirty_days_ago = today - timedelta(days=30)
    last_30_days_expenses = (
        Expense.objects
        .filter(paid_by=user, created_at__date__gte=thirty_days_ago)
    )
    
    # CATEGORY DATA - Categorize expenses by description keywords
    category_keywords = {
        "Food": ["food", "lunch", "dinner", "breakfast", "pizza", "restaurant", "cafe", "snacks", "grocery", "meal"],
        "Bills": ["bill", "electricity", "water", "internet", "phone", "utility"],
        "Travel": ["transport", "uber", "taxi", "bus", "fuel", "petrol", "auto", "travel", "flight", "train"],
        "Shopping": ["shopping", "clothes", "dress", "shoes", "mall", "store", "purchase"],
        "Other": []
    }
    
    category_totals = {cat: 0 for cat in category_keywords.keys()}
    
    for expense in last_30_days_expenses:
        description_lower = expense.description.lower()
        categorized = False
        
        for category, keywords in category_keywords.items():
            if category != "Other" and any(keyword in description_lower for keyword in keywords):
                category_totals[category] += float(expense.amount)
                categorized = True
                break
        
        if not categorized:
            category_totals["Other"] += float(expense.amount)
    
    # Prepare category data for chart with specific colors
    category_colors_map = {
        "Food": "#4ECDC4",      # Green/Teal
        "Bills": "#FF6B6B",     # Red/Coral
        "Travel": "#45B7D1",    # Blue
        "Shopping": "#98D8C8",  # Mint
        "Other": "#B0B0B0"      # Grey
    }
    
    category_labels = []
    category_amounts = []
    category_colors = []
    total_30_days = 0
    
    for category in ["Food", "Bills", "Travel", "Shopping", "Other"]:
        amount = category_totals[category]
        if amount > 0:
            category_labels.append(category)
            category_amounts.append(amount)
            category_colors.append(category_colors_map[category])
            total_30_days += amount
    
    # Prepare JSON data for charts
    import json
    
    new_charts_json = json.dumps({
        "owe_vs_owed": {
            "labels": period_labels,
            "you_owe": you_owe_data,
            "you_are_owed": you_are_owed_data
        },
        "category_breakdown": {
            "labels": category_labels,
            "amounts": category_amounts,
            "colors": category_colors,
            "total": round(total_30_days, 2)
        }
    })

    context = {
        "notification": notification,   # PASS TO TEMPLATE
        "total_groups": total_groups,
        "total_expenses": total_expenses,
        "groups": groups,
        "recent_expenses": recent_expenses,
        "week_options": week_options,
        "total_paid": f"{total_paid:.2f}",
        "total_need_to_pay": f"{total_need_to_pay:.2f}",
        "total_will_get_back": f"{total_will_get_back:.2f}",
        "new_charts_json": new_charts_json,  # NEW CHARTS DATA
        "chart_period": chart_period,        # SELECTED PERIOD
        "chart": {
            "labels": paid_labels,
            "paid": paid_values,
            "need_to_pay": need_values,
            "will_get_back": getback_values,
            "weekly_labels": week_labels,
            "weekly_income": income_by_week,
            "weekly_outcome": outcome_by_week,
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

            # ADD SUCCESS MESSAGE (THIS TRIGGERS TOAST)
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
    



@login_required
def report(request):
    user = request.user

    # ---------------- FILTERS ----------------
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    expenses = Expense.objects.filter(group__members=user)

    if from_date and to_date:
        expenses = expenses.filter(created_at__date__range=[from_date, to_date])

    expenses = expenses.order_by("-created_at")

    # ---------------- SUMMARY ----------------
    total_paid = (
        expenses
        .filter(paid_by=user)
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    need_to_pay = (
        ExpenseSplit.objects
        .filter(user=user)
        .exclude(expense__paid_by=user)
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    will_get_back = (
        ExpenseSplit.objects
        .filter(expense__paid_by=user)
        .exclude(user=user)
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    balance = will_get_back - need_to_pay

    # ---------------- GROUP WISE REPORT ----------------
    group_report = []

    groups = Group.objects.filter(members=user)

    for group in groups:
        total = Expense.objects.filter(group=group).aggregate(Sum("amount"))["amount__sum"] or 0

        paid = Expense.objects.filter(
            group=group,
            paid_by=user
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        get_back = ExpenseSplit.objects.filter(
            expense__group=group,
            expense__paid_by=user
        ).exclude(user=user).aggregate(Sum("amount"))["amount__sum"] or 0

        need_pay = ExpenseSplit.objects.filter(
            expense__group=group,
            user=user
        ).exclude(expense__paid_by=user).aggregate(Sum("amount"))["amount__sum"] or 0

        group_report.append({
            "group": group.title,
            "total": total,
            "paid": paid,
            "get_back": get_back,
            "need_pay": need_pay,
        })


    # ---------------- CONTEXT ----------------
    context = {
        "expenses": expenses,   # first 6 only
        "total_paid": total_paid,
        "need_to_pay": need_to_pay,
        "will_get_back": will_get_back,
        "balance": balance,
        "group_report": group_report,
        "all_expenses": expenses,   # for view more
    }

    return render(request, "accounts/report.html", context)






@login_required
def report_pdf(request):
    user = request.user

    expenses = Expense.objects.filter(group__members=user).order_by("-created_at")

    total_paid = expenses.filter(paid_by=user).aggregate(Sum("amount"))["amount__sum"] or 0

    need_to_pay = (
        ExpenseSplit.objects
        .filter(user=user)
        .exclude(expense__paid_by=user)
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    will_get_back = (
        ExpenseSplit.objects
        .filter(expense__paid_by=user)
        .exclude(user=user)
        .aggregate(Sum("amount"))["amount__sum"] or 0
    )

    balance = will_get_back - need_to_pay

    template = get_template("accounts/report_pdf.html")

    html = template.render({
        "user": user,
        "expenses": expenses,
        "total_paid": total_paid,
        "need_to_pay": need_to_pay,
        "will_get_back": will_get_back,
        "balance": balance,
        "date": timezone.now(),
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Expense_Report.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response



