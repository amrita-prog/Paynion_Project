from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import qrcode
import io
import base64


from .models import Payment

User = get_user_model()


@login_required
def upi_pay(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    to_user_id = request.POST.get("to_user_id")
    amount = request.POST.get("amount")

    to_user = get_object_or_404(User, id=to_user_id)

    if not to_user.upi_id:
        return HttpResponseBadRequest("Receiver UPI not set")

    payment = Payment.objects.create(
        payer=request.user,
        receiver=to_user,
        amount=amount,
        upi_id=to_user.upi_id,
        status="PENDING"
    )

    upi_link = (
        f"upi://pay?"
        f"pa={to_user.upi_id}&"
        f"pn={to_user.full_name}&"
        f"am={amount}&"
        f"cu=INR"
    )

    # 🔹 QR Code for desktop
    qr = qrcode.make(upi_link)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "payments/upi_redirect.html", {
        "upi_link": upi_link,
        "qr_code": qr_base64,
        "payment": payment
    })
