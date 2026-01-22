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
from accounts.models import Notification
import os
import uuid
from .ai_utils import extract_bill_data
from django.http import JsonResponse
from django.conf import settings

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

            # Clear old splits (safety)
            expense.splits.all().delete()

            if expense.split_type == "equal":
                handle_equal_split(expense, users)

            elif expense.split_type == "percentage":
                handle_percentage_split(expense, users, request.POST)

            elif expense.split_type == "custom":
                handle_custom_split(expense, users, request.POST)

            # CREATE NOTIFICATIONS (IMPORTANT PART)
            for member in users:
                if member != request.user:
                    Notification.objects.create(
                        user=member,
                        message=f"₹{expense.amount} added in group '{group.title}'"
                    )

            return redirect("groups:group_detail", group.id)

    else:
        form = ExpenseForm(group=group)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "group": group
    })




@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    # Permission check
    if request.user != expense.paid_by:
        return redirect("groups:group_detail", group_id=expense.group.id)

    group = expense.group

    # Get users involved in this expense (except deleter)
    split_users = expense.splits.exclude(user=request.user)

    if request.method == "POST":

        # Send notification to other users
        for split in split_users:
            Notification.objects.create(
                user=split.user,
                message=f"Expense '{expense.description}' was deleted in group {group.name}"
            )

        expense.delete()

    return redirect("groups:group_detail", group_id=group.id)




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



@login_required
def scan_bill(request):
    """
    AJAX endpoint for bill image scanning and OCR extraction.
    
    Expects: POST request with "bill" file field
    Returns: JSON with success status, extracted amount & description
    """
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Only POST requests allowed"
        })
    
    if not request.FILES.get("bill"):
        return JsonResponse({
            "success": False,
            "message": "No bill image provided"
        })
    
    try:
        bill = request.FILES["bill"]
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save uploaded file temporarily
        import uuid
        temp_filename = f"{uuid.uuid4()}_{bill.name}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        with open(temp_path, "wb+") as f:
            for chunk in bill.chunks():
                f.write(chunk)
        
        # Extract bill data using AI
        result = extract_bill_data(temp_path)
        
        # Clean up temp file (if not already cleaned by extract_bill_data)
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        if not result["success"]:
            return JsonResponse({
                "success": False,
                "message": result.get("message", "Failed to extract bill data")
            })
        
        # Return clean JSON response
        return JsonResponse({
            "success": True,
            "amount": result["amount"],  # Numeric value, not string
            "description": result["title"]
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error processing bill: {str(e)}"
        })