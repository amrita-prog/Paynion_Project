from decimal import Decimal
from .models import ExpenseSplit


def handle_equal_split(expense, users):
    per_person = expense.amount / len(users)

    for user in users:
        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount=per_person
        )


def handle_percentage_split(expense, users, post_data):
    """
    post_data:
    percent_<user_id> = value
    """

    total_percent = Decimal("0")

    for user in users:
        percent = post_data.get(f"percent_{user.id}")

        if not percent:
            raise ValueError("Percentage missing")

        percent = Decimal(percent)
        total_percent += percent

        amount = (percent / Decimal("100")) * expense.amount

        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount=amount
        )

    if total_percent != 100:
        raise ValueError("Total percentage must be 100")


def handle_custom_split(expense, users, post_data):
    total_amount = Decimal("0")

    for user in users:
        amount = post_data.get(f"amount_{user.id}")

        if not amount:
            raise ValueError("Custom amount missing")

        amount = Decimal(amount)
        total_amount += amount

        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount=amount
        )

    if total_amount != expense.amount:
        raise ValueError("Custom split total must equal expense amount")
