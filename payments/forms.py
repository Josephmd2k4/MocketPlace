from django import forms

class PayoutForm(forms.Form):
    email = forms.EmailField(label="Recipient Email")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    note = forms.CharField(widget=forms.Textarea, required=False)
    currency = forms.ChoiceField(choices=[('USD', 'USD')])