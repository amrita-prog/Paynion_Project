from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Settlement, PaymentHistory
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

    # QR Code for desktop
    qr = qrcode.make(upi_link)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "payments/upi_redirect.html", {
        "upi_link": upi_link,
        "qr_code": qr_base64,
        "payment": payment
    })






@login_required
def mark_as_paid(request, settlement_id):
    settlement = get_object_or_404(Settlement, id=settlement_id)

    if request.user != settlement.payer:
        messages.error(request, "You are not allowed.")
        return redirect("accounts:dashboard")
    
    payment_mode = request.POST.get("payment_mode")

    if payment_mode not in ["UPI", "CASH"]:
        messages.error(request, "Please select payment mode.")
        return redirect("groups:group_detail", group_id=settlement.group.id)
    
    settlement.payment_mode = payment_mode
    settlement.status = "PAID_REQUESTED"
    settlement.paid_requested_at = timezone.now()
    settlement.save()

    messages.success(request, "Payment request sent to receiver.")
    return redirect("groups:group_detail", group_id=settlement.group.id)




@login_required
def accept_payment(request, settlement_id):
    settlement = get_object_or_404(Settlement, id=settlement_id)

    if request.user != settlement.receiver:
        messages.error(request, "You are not allowed.")
        return redirect("dashboard")

    settlement.status = "SETTLED"
    settlement.settled_at = timezone.now()
    settlement.save()

    PaymentHistory.objects.create(
        settlement=settlement,
        paid_by=settlement.payer,
        received_by=settlement.receiver,
        amount=settlement.amount,
        payment_mode=settlement.payment_mode,
        requested_at=settlement.paid_requested_at
    )

    settlement.group.last_settled_at = settlement.settled_at
    settlement.group.save()

    messages.success(request, "Payment confirmed successfully.")
    return redirect("groups:group_detail", group_id=settlement.group.id)





@login_required
def reject_payment(request, settlement_id):
    settlement = get_object_or_404(Settlement, id=settlement_id)

    if request.user != settlement.receiver:
        messages.error(request, "You are not allowed.")
        return redirect("dashboard")

    settlement.status = "PENDING"
    settlement.paid_requested_at = None
    settlement.save()

    messages.info(request, "Payment rejected. Settlement reopened.")
    return redirect("groups:group_detail", group_id=settlement.group.id)




@login_required
def payment_history(request):
    history = PaymentHistory.objects.filter(
        paid_by=request.user
    ) | PaymentHistory.objects.filter(
        received_by=request.user
    )

    history = history.select_related(
        "paid_by", "received_by", "settlement", "settlement__group"
    ).order_by("-confirmed_at")

    return render(request, "payments/payment_history.html", {
        "history": history
    })
