from django.db.models import Sum
from .models import Expense, ExpenseSplit   
from collections import defaultdict


def calculate_user_balance(user):
    paid = Expense.objects.filter(paid_by=user).aggregate(total=Sum('amount'))['total'] or 0
    owed = ExpenseSplit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    return paid - owed  



def calculate_group_balances(group):
    balances = defaultdict(float)

    for expense in group.expenses.all():
        # Person who paid
        balances[expense.paid_by] += float(expense.amount)

        # People who owe
        for split in expense.splits.all():
            balances[split.user] -= float(split.amount)

    return dict(balances)
