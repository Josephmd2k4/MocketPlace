import stripe
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from models import Order

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Use your actual webhook secret from Django settings
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
        # Construct the event 
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponseBadRequest()
    
    # Handle the checkout.session.completed event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        
        # Retrieve the order ID from metadata
        order_id = intent['metadata'].get('order_id')
        
        if order_id:
            try:
                # Fetch and update the order
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
            except Order.DoesNotExist:
                # Log the error or handle the case where order is not found
                print(f"Order with ID {order_id} not found")
    
    return HttpResponse(status=200)