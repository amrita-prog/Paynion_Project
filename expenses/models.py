from django.db import models
from django.conf import settings
from groups.models import Group

User = settings.AUTH_USER_MODEL


class Expense(models.Model):
    SPLIT_TYPES = [
        ("equal", "Equal"),
        ("percentage", "Percentage"),
        ("custom", "Custom"),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="paid_expenses"
    )

    split_between = models.ManyToManyField(
        User,
        related_name="split_expenses"
    )

    split_type = models.CharField(
        max_length=20,
        choices=SPLIT_TYPES,
        default="equal"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"
