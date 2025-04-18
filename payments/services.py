import paypalrestsdk, time, uuid
from django.conf import settings
from datetime import datetime
from django.shortcuts import get_object_or_404
from posts.models import Post

# Configure the SDK
paypalrestsdk.configure({
    "mode": 'sandbox', 
    "client_id": 'AR-8QjzWUOHJdpjWTMqTFgtvExqk42tC2wPZLNp-qFHGHqjV11VAVEFzqe_HbvyzituEcGSWxWtok6sD',
    "client_secret": 'EI0eUZjgUu5lfgCHzWuHswCylR2ZSimbAhfzOwV4ed7tdhlVRMWGcuZ4CMajmpkMajQwis6iI3Ov4Uao'
})

def send_payout(post_id, amount, currency="USD"):
    post = get_object_or_404(Post, id=post_id)
    user_email = post.user.email

    payout = paypalrestsdk.Payout({
        "sender_batch_header": {
            "sender_batch_id": str(uuid.uuid4()),
            "email_subject": "New Transaction!",
            "email_message": "You have received a transaction. Thanks for using FSC Mocketplace!"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": str(amount)
                },
                "receiver": user_email,
                "note": "Transaction for {post.title}"
            }
        ]
    })

    if payout.create(sync_mode=False):
        payout_id = payout["batch_header"]["payout_batch_id"]
        print("Payout created successfully :D")

        # Save to the database
        Payout.objects.create(
            payout_id=payout_id,
            amount=amount,
            status="PENDING"
        )

        return payout

    else:
        print("Payout creation failed: ", payout.error)
        return None

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