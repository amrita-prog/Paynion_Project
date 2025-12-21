from django.db.models import Sum
from .models import Expense, ExpenseSplit   

def calculate_user_balance(user):
    paid = Expense.objects.filter(paid_by=user).aggregate(total=Sum('amount'))['total'] or 0
    owed = ExpenseSplit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    return paid - owed  