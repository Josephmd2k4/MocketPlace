from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from payments.models import Order
from django.core.mail import send_mail

@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == "Completed":
        # Validate payment
        try:
            order = Order.objects.get(invoice=ipn_obj.invoice)
        except Order.DoesNotExist:
            return

        if ipn_obj.mc_gross == order.amount and \
           ipn_obj.mc_currency == "USD" and \
           ipn_obj.receiver_email == "your-paypal-email@example.com":
            
            if not order.paid:
                order.paid = True
                order.transaction_id = ipn_obj.txn_id
                order.save()

                # Optional: send confirmation
                send_mail(
                    'Payment Received',
                    f'Your order {order.id} has been paid successfully.',
                    'you@example.com',
                    [order.user.email]
                )
    else:
        # Handle other statuses (e.g., Pending, Failed, Refunded)
        pass