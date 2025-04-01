from django.shortcuts import render
import json
from django.http import JsonResponse
from .payout import send_payout
from django.views.decorators.csrf import csrf_exempt
from .models import Payout
import paypalrestsdk

@csrf_exempt
def paypal_webhook(request):
    if request.method == "POST":
        # Parse the incoming webhook JSON
        data = json.loads(request.body)
        event_type = data.get("event_type")
        resource = data.get("resource", {})

        # Verify the webhook signature (optional but recommended)
        if not verify_webhook_signature(request):
            return JsonResponse({"status": "error", "message": "Invalid signature"}, status=400)

        # Handle different event types
        if event_type == "PAYMENT.PAYOUTSBATCH.SUCCESS":
            # Handle successful payout event
            payout_batch_id = resource.get("payout_batch_id")
            Payout.objects.filter(payout_id=payout_batch_id).update(status="SUCCESS")
            return JsonResponse({"status": "success", "message": "Payout success"})

        elif event_type == "PAYMENT.PAYOUTSBATCH.DENIED":
            # Handle failed payout event
            payout_batch_id = resource.get("payout_batch_id")
            Payout.objects.filter(payout_id=payout_batch_id).update(status="FAILED")
            return JsonResponse({"status": "success", "message": "Payout failed"})

        # Add more events as needed
        return JsonResponse({"status": "error", "message": "Unhandled event type"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def verify_webhook_signature(request): 
    # Implement PayPal signature verification (optional but recommended for security)
    return True  # Placeholder, implement signature verification here if needed

def payout_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        payout = send_payout(email, amount)

        if payout:
            return JsonResponse({"status": "success", "payout_id": payout["batch_header"]["payout_batch_id"]})
        else:
            return JsonResponse({"status": "error"}, status=400)
        
def payout_status_view(request):
    payouts = Payout.objects.all()
    return render(request, "payout_status.html", {"payouts":payouts})

