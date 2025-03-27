import os
import django
from flask import Flask, request, jsonify
import stripe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MocketPlace.settings')
django.setup()

from payments.models import Order

flask_app = Flask(__name__)

# Stripe secret key
stripe.api_key = 'sk_test_51R4r9IQMpcz9rN0YeNF4Ctw8XY9ZPa56AkgOfc70zixvbFcZ5efeaWRF8cd1yY4zJjlhgpQVvFXW4GbnmUjutqyd000uZOe2QV'

# Create a payment intent
@flask_app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        amount = data.get('amount', 500) # Default to $5 for now

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={'enabled': True},
        )
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Stripe webhook endpoint
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = 'whsec_...'  # Your webhook secret
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception as e:
        return jsonify(success=False), 400

    # Handle event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")

    return jsonify(success=True)

if event['type'] == 'payment_intent.succeeded':
    order_id = intent['metadata']['order_id']

    if order_id:
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()
