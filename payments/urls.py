from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("upi-pay/", views.upi_pay, name="upi_pay"),
    path("settlement/<int:settlement_id>/paid/", views.mark_as_paid, name="mark_as_paid"),
    path("settlement/<int:settlement_id>/accept/", views.accept_payment, name="accept_payment"),
    path("settlement/<int:settlement_id>/reject/", views.reject_payment, name="reject_payment"),
    path("history/", views.payment_history, name="payment_history"),
]