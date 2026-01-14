from django.db import models
from django.conf import settings
from groups.models import Group

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





class Settlement(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="settlements"
    )
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments_to_make")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments_to_receive")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID_REQUESTED", "Paid Requested"),
            ("SETTLED", "Settled"),
        ],
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    paid_requested_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)




class PaymentHistory(models.Model):
    settlement = models.OneToOneField(
        Settlement, on_delete=models.CASCADE
    )
    paid_by = models.ForeignKey(
        User, related_name="paid_history", on_delete=models.CASCADE
    )
    received_by = models.ForeignKey(
        User, related_name="received_history", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(
        max_length=20, choices=[("UPI", "UPI"), ("CASH", "Cash")]
    )

    requested_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(auto_now_add=True)
