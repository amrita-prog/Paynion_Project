from django.db.models import Sum
from .models import Expense, ExpenseSplit   
from collections import defaultdict
from decimal import Decimal


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




def calculate_settlements(balances):
    """
    balances = {
        user1: Decimal('1028.00'),
        user2: Decimal('-800.00'),
        user3: Decimal('-228.00'),
    }
    """

    creditors = []
    debtors = []

    # Separate users
    for user, amount in balances.items():
        if amount > 0:
            creditors.append([user, amount])
        elif amount < 0:
            debtors.append([user, -amount])  # store positive debt

    settlements = []

    i = j = 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        settled_amount = min(debt, credit)

        settlements.append({
            "from": debtor,
            "to": creditor,
            "amount": settled_amount
        })

        debtors[i][1] -= settled_amount
        creditors[j][1] -= settled_amount

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements




def calculate_settlements(balances):
    """
    balances = {
        user1: Decimal('1028.00'),
        user2: Decimal('-800.00'),
        user3: Decimal('-228.00'),
    }
    """

    creditors = []
    debtors = []

    # Separate users
    for user, amount in balances.items():
        if amount > 0:
            creditors.append([user, amount])
        elif amount < 0:
            debtors.append([user, -amount])  # store positive debt

    settlements = []

    i = j = 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        settled_amount = min(debt, credit)

        settlements.append({
            "from": debtor,
            "to": creditor,
            "amount": settled_amount
        })

        debtors[i][1] -= settled_amount
        creditors[j][1] -= settled_amount

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
