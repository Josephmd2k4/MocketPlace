from django import forms
from paypal.standard.forms import PayPalPaymentsForm

class PaymentForm(forms.Form):
    amount = forms.DecimalField()
    item_name = forms.CharField()
        
def __init__(self, *args, **kwargs):
    request = kwargs.pop('request', None)
    super().__init__(*args, **kwargs)
    if request:
        self.fields['paypal_form'] = PayPalPaymentsForm(initial={
            'business': 'cjefferys@mocs.flsouthern.edu',
            'amount': self.initial.get('amount', 0),
            'post_title': self.initial.get('post_title', ''),
            'unique_post_id': self.initial.get('post_id'),
            'notify_url': request.build_absolute_uri('paypal/'),
            'return_url': request.build_absolute_uri('checkout/<int:post_id>/'),
            'cancel_return': request.build_absolute_uri('cancel/'),
            'currency_code': 'USD',
        })