from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from .forms import SignUpForm
from django.contrib.auth import login, logout, authenticate 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from groups.models import Group, GroupInvite
from expenses.models import Expense, ExpenseSplit
from django.db.models import Sum

User = get_user_model()


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})



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

            # 🔥 MAIN FIX
            if next_url:
                return redirect(next_url)

            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html", {"next": next_url})



@login_required
def dashboard(request):
    total_groups = Group.objects.filter(members=request.user).count()
    total_expenses = Expense.objects.filter(paid_by=request.user).count()

    pending_invites = GroupInvite.objects.filter(
        email=request.user.email,
        is_accepted=False
    )

    recent_expenses = Expense.objects.filter(paid_by=request.user).order_by('-created_at')

    balance = 0  

    return render(request, "accounts/dashboard.html", {
        "total_groups": total_groups,
        "total_expenses": total_expenses,
        "recent_expenses": recent_expenses,
        "balance": balance,
    })


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