from django.db import models
from django.conf import settings

# Create your models here.

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paid_by_me")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_by_me")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ],
        default="PENDING"
    )
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
