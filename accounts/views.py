from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from .forms import SignUpForm
from django.contrib.auth import login, logout, authenticate 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from groups.models import Group
from expenses.models import Expense

User = get_user_model()


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})



def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Match email to username for authentication
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


@login_required
def dashboard(request):
    total_groups = Group.objects.filter(members=request.user).count()
    total_expenses = Expense.objects.filter(paid_by=request.user).count()

    recent_expenses = Expense.objects.filter(paid_by=request.user).order_by('-created_at')[:5]

    balance = 0  

    return render(request, "accounts/dashboard.html", {
        "total_groups": total_groups,
        "total_expenses": total_expenses,
        "recent_expenses": recent_expenses,
        "balance": balance,
    })


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")