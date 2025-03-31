from django.shortcuts import render
from django.http import JsonResponse
from .paypal_utils import send_payout

def payout_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        payout = send_payout(email, amount)

        if payout:
            return JsonResponse({"status": "success", "payout_id": payout["batch_header"]["payout_batch_id"]})
        else:
            return JsonResponse({"status": "error"}, status=400)

