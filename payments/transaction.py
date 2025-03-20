import os
from flask import Flask, jsonify, redirect, request

import stripe
stripe.api_key = 'pk_test_51R4r9IQMpcz9rN0YkNDxUYJNSa0KWfAMoDsz79SjBCX8p1Ese5nnJRAjjaXedTjeARvk8CTIMVAVgpoH4loGiqJx00EY6soAy5'

app = Flask(__name__,
            static_url_path='',
            static_folder='public')

domain = '127.0.0.1'

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            ui_mode = 'embedded',
            line_items=[
                {
                    'price': '{{PRICE_ID}}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            return_url=domain + '/return.html?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=session.client_secret)

@app.route('/session-status', methods=['GET'])
def session_status():
  session = stripe.checkout.Session.retrieve(request.args.get('session_id'))

  return jsonify(status=session.status, customer_email=session.customer_details.email)

if __name__ == '__main__':
    app.run(port=4242)