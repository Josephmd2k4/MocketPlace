import paypalrestsdk
import time
from .models import Payout
import requests

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
