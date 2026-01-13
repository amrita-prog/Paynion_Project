from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("upi-pay/", views.upi_pay, name="upi_pay")
]