from django.shortcuts import render
import json
from django.http import JsonResponse
from .payout import send_payout
from django.views.decorators.csrf import csrf_exempt
from .models import Payout
import paypalrestsdk
from django.utils import timezone
from .services import get_all, get_payout_details, create_payout
from datetime import datetime, timedelta
from .forms import PayoutForm
from django.contrib import messages
from django.shortcuts import redirect

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
        
def transact_status_view(request):
    # Get filter parameters from request
    status_filter = request.GET.get('status')
    days = request.GET.get('days', 30)  # Default to last 30 days
    
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    # Calculate date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get payouts from PayPal
    payouts_data = get_all(
        start_date=start_date,
        end_date=end_date,
        status=status_filter
    )
    
    # Process payouts into a format for the template
    payouts = []
    if payouts_data and hasattr(payouts_data, 'items'):
        for item in payouts_data.items:
            # This structure depends on the exact response format from PayPal
            # Adjust according to what your API returns
            payout = {
                'payout_id': item.get('payout_item_id', ''),
                'email': item.get('receiver', ''),
                'amount': item.get('amount', {}).get('value', 0),
                'status': item.get('transaction_status', '').lower()
            }
            payouts.append(payout)
    
    return render(request, 'payments/transact_status.html', {
        'payouts': payouts,
        'status_filter': status_filter,
        'days': days
    })

def create_new_payout(request):
    if request.method == 'POST':
        form = PayoutForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data['note']
            currency = form.cleaned_data['currency']
            
            payout_result = create_payout(email, amount, note, currency)
            
            if payout_result:
                messages.success(request, f"Payout initiated successfully to {email}")
                return redirect('payout_status')
            else:
                messages.error(request, "Failed to create payout. Please check logs.")
    else:
        form = PayoutForm()
    
    return render(request, 'payments/checkout.html', {'form': form})
