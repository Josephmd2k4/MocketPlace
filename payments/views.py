from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import Payout
import paypalrestsdk
from django.utils import timezone
from .services import get_all, get_payout_details, create_payout
from datetime import datetime, timedelta
from .forms import PayoutForm
from django.contrib import messages
from django.shortcuts import redirect
import paypalrestsdk
import time, datetime, requests

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

def send_payout(receiver_email, amount, currency="USD"):
    payout = paypalrestsdk.Payout({
        "sender_batch_header": {
            "sender_batch_id": "batch_" + str(int(time.time())),
            "email_subject": "You have received a payout!"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": str(amount),
                    "currency": currency
                },
                "receiver": receiver_email,
                "note": "Thanks for using FSC Mocketplace!",
                "sender_item_id": "item_" + str(int(time.time()))
            }
        ]
    })

    if payout.create():
        payout_id = payout["batch_header"]["payout_batch_id"]

        # Save to the database
        Payout.objects.create(
            payout_id=payout_id,
            email=receiver_email,
            amount=amount,
            currency=currency,
            status="PENDING"
        )

        return payout
    else:
        print(payout.error)
        return None

def cancel_item():
    url = "https://api.sandbox.paypal.com/v1/payments/payouts-item/N2CD2335SGSN8/cancel"

    headers = {
        'authorization': "Bearer A21AAIjI8oesIez25W1wyT2fo4swHAQQ8abYOhaPpOtCDQI7h8-KMRdQVOrQy8Zd4W0hD_YQbp6ou-iZAvuXJmMfXXAzR-jLA",
        'content-type': "application/json"
        }

    response = requests.request("POST", url, headers=headers)

    print(response.status_code)

    print(response.text)

    {
    "name": "ITEM_INCORRECT_STATUS",
    "message": "Only items in Unclaimed status can be cancelled.",
    "debug_id": "a37b003497d53",
    "information_link": "https://developer.paypal.com/docs/api/payments.payouts-batch/#errors",
    "links": []
    }

def batch_details():
    url = "https://api.sandbox.paypal.com/v1/payments/payouts/KWRCQ89XV4Q3U"

    headers = {
        'authorization': "Bearer A21AAIjI8oesIez25W1wyT2fo4swHAQQ8abYOhaPpOtCDQI7h8-KMRdQVOrQy8Zd4W0hD_YQbp6ou-iZAvuXJmMfXXAzR-jLA",
        'content-type': "application/json"
        }

    response = requests.request("GET", url, headers=headers)

    print(response.status_code)

    print(response.text)

    {
  "batch_header": {
    "payout_batch_id": "KWRCQ89XV4Q3U",
    "batch_status": "SUCCESS",
    "time_created": "2018-04-24T16:26:21Z",
    "time_completed": "2018-04-24T16:26:37Z",
    "time_closed": "2018-04-24T16:26:37Z",
    "sender_batch_header": {
      "sender_batch_id": "batch-1524587181541",
      "email_subject": "You have a payment"
    },
    "funding_source": "BALANCE",
    "amount": {
      "currency": "USD",
      "value": "3.00"
    },
    "fees": {
      "currency": "USD",
      "value": "0.25"
    }
  },
  "items": [
    {
      "payout_item_id": "YBHMKGZY6WEU6",
      "transaction_id": "4PR52677YY938730R",
      "transaction_status": "SUCCESS",
      "payout_item_fee": {
        "currency": "USD",
        "value": "0.25"
      },
      "payout_batch_id": "KWRCQ89XV4Q3U",
      "payout_item": {
        "recipient_type": "PHONE",
        "amount": {
          "currency": "USD",
          "value": "1.00"
        },
        "note": "Payouts sample transaction",
        "receiver": "4087811638",
        "sender_item_id": "item-1524587181541",
        "recipient_wallet": "PAYPAL"
      },
      "time_processed": "2018-04-24T16:26:34Z",
      "links": [
        {
          "href": "https://api.sandbox.paypal.com/v1/payments/payouts-item/YBHMKGZY6WEU6",
          "rel": "item",
          "method": "GET",
          "encType": "application/json"
        }
      ]
    },
    {
      "payout_item_id": "N2CD2335SGSN8",
      "transaction_status": "FAILED",
      "payout_item_fee": {
        "currency": "USD",
        "value": "0.00"
      },
      "payout_batch_id": "KWRCQ89XV4Q3U",
      "payout_item": {
        "recipient_type": "EMAIL",
        "amount": {
          "currency": "USD",
          "value": "1.00"
        },
        "note": "Payouts sample transaction",
        "receiver": "ps-rec@paypal.com",
        "sender_item_id": "item-1524587181541",
        "recipient_wallet": "PAYPAL"
      },
      "time_processed": "2018-04-24T16:26:21Z",
      "errors": {
        "name": "DUPLICATE_ITEM",
        "message": "This is a duplicate item as the REF_ID matches with another item in the batch Payout. The REF_ID should be unique for each Payout.",
        "information_link": "https://developer.paypal.com/docs/api/payments.payouts-batch/#errors",
        "details": [],
        "links": []
      },
      "links": [
        {
          "href": "https://api.sandbox.paypal.com/v1/payments/payouts-item/N2CD2335SGSN8",
          "rel": "item",
          "method": "GET",
          "encType": "application/json"
        }
      ]
    },
    {
      "payout_item_id": "JHECFASGRYFN2",
      "transaction_status": "FAILED",
      "payout_item_fee": {
        "currency": "USD",
        "value": "0.00"
      },
      "payout_batch_id": "KWRCQ89XV4Q3U",
      "payout_item": {
        "recipient_type": "PAYPAL_ID",
        "amount": {
          "currency": "USD",
          "value": "1.00"
        },
        "note": "Payouts sample transaction",
        "receiver": "FSMRBANCV8PSG",
        "sender_item_id": "item-1524587181541",
        "recipient_wallet": "PAYPAL"
      },
      "time_processed": "2018-04-24T16:26:21Z",
      "errors": {
        "name": "DUPLICATE_ITEM",
        "message": "This is a duplicate item as the REF_ID matches with another item in the batch Payout. The REF_ID should be unique for each Payout.",
        "information_link": "https://developer.paypal.com/docs/api/payments.payouts-batch/#errors",
        "details": [],
        "links": []
      },
      "links": [
        {
          "href": "https://api.sandbox.paypal.com/v1/payments/payouts-item/JHECFASGRYFN2",
          "rel": "item",
          "method": "GET",
          "encType": "application/json"
        }
      ]
    }
  ],
  "links": [
    {
      "href": "https://api.sandbox.paypal.com/v1/payments/payouts/KWRCQ89XV4Q3U?page_size=1000&page=1",
      "rel": "self",
      "method": "GET",
      "encType": "application/json"
    }
  ]
}

import paypalrestsdk
from django.conf import settings
from datetime import datetime

# Configure the SDK
paypalrestsdk.configure({
    "mode": 'sandbox', 
    "client_id": 'AR-8QjzWUOHJdpjWTMqTFgtvExqk42tC2wPZLNp-qFHGHqjV11VAVEFzqe_HbvyzituEcGSWxWtok6sD',
    "client_secret": 'EI0eUZjgUu5lfgCHzWuHswCylR2ZSimbAhfzOwV4ed7tdhlVRMWGcuZ4CMajmpkMajQwis6iI3Ov4Uao'
})

def get_payout_details(payout_batch_id):
    """Get details for a specific payout batch"""
    try:
        payout = paypalrestsdk.Payout.find(payout_batch_id)
        return payout
    except Exception as e:
        print(f"Error fetching payout {payout_batch_id}: {e}")
        return None

def get_item_details(payout_item_id):
    """Get details for a specific payout item"""
    try:
        payout_item = paypalrestsdk.PayoutItem.find(payout_item_id)
        return payout_item
    except Exception as e:
        print(f"Error fetching payout item {payout_item_id}: {e}")
        return None

def get_all(start_date=None, end_date=None, status=None):
    """
    Get all payouts with optional filtering
    Note: PayPal API may have limitations on date ranges and pagination
    """
    # Implementation depends on the specific PayPal SDK version you're using
    # This is a placeholder based on common PayPal API patterns
    params = {}
    
    if start_date:
        params['start_time'] = start_date.isoformat()
    if end_date:
        params['end_time'] = end_date.isoformat()
    if status:
        params['status'] = status
        
    try:
        # This is a placeholder - check PayPal SDK docs for exact implementation
        payouts = paypalrestsdk.Payout.all(params)
        return payouts
    except Exception as e:
        print(f"Error fetching payouts: {e}")
        return []

def create_payout(email, amount, note="Thank you!", currency="USD"):
    """Create a new payout to a recipient"""
    payout = {
        "sender_batch_header": {
            "sender_batch_id": f"batch_{datetime.now().timestamp()}",
            "email_subject": "You have a payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": str(amount),
                    "currency": currency
                },
                "note": note,
                "receiver": email,
                "sender_item_id": f"item_{datetime.now().timestamp()}"
            }
        ]
    }
    
    try:
        payout_batch = paypalrestsdk.Payout(payout)
        if payout_batch.create():
            return payout_batch
        else:
            print(payout_batch.error)
            return None
    except Exception as e:
        print(f"Error creating payout: {e}")
        return None

@csrf_protect
def payout_form(request):
    """View to display and handle the payout form"""
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        amount = request.POST.get('amount')
        note = request.POST.get('note', 'Thank you for your work!')
        currency = request.POST.get('currency', 'USD')
        reference = request.POST.get('reference', '')
        
        # Validate inputs
        if not email or not amount:
            messages.error(request, "Email and amount are required fields")
            return render(request, 'payout_form.html')
        
        try:
            # Convert amount to float for validation
            amount_float = float(amount)
            if amount_float <= 0:
                messages.error(request, "Amount must be greater than zero")
                return render(request, 'payout_form.html')
                
            # Create the payout structure
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": f"batch_{datetime.now().timestamp()}",
                    "email_subject": "You have received a payment"
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": str(amount),
                            "currency": currency
                        },
                        "note": note,
                        "receiver": email,
                        "sender_item_id": f"item_{datetime.now().timestamp()}"
                    }
                ]
            }
            
            # Create the payout via PayPal API
            payout_batch = paypalrestsdk.Payout(payout_data)
            if payout_batch.create():
                # Save payout details to database
                batch_id = payout_batch.batch_header.payout_batch_id
                payout = Payout.objects.create(
                    payout_id=batch_id,
                    receiver_email=email,
                    amount=amount_float,
                    currency=currency,
                    note=note,
                    reference=reference,
                    status="PENDING"
                )
                
                messages.success(request, f"Payout initiated successfully! Batch ID: {batch_id}")
                return redirect('payout_success', payout_id=payout.id)
            else:
                # Handle API error
                error_message = payout_batch.error.get('message', 'An error occurred')
                messages.error(request, f"Failed to create payout: {error_message}")
                return render(request, 'payout_form.html')
                
        except ValueError:
            messages.error(request, "Please enter a valid amount")
            return render(request, 'payout_form.html')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return render(request, 'payout_form.html')
    
    # GET request - just display the form
    return render(request, 'payout_form.html')