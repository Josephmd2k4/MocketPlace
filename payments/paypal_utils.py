import paypalrestsdk
import time

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
                "note": "Thanks for using our marketplace!",
                "sender_item_id": "item_" + str(int(time.time()))
            }
        ]
    })

    if payout.create():
        print("Payout created successfully")
        return payout
    else:
        print(payout.error)
        return None
