from django import forms


class AddMoneyForm(forms.Form):
    amount = forms.DecimalField(
        min_value=1,
        max_digits=10,
        decimal_places=2,
        label="Amount to add (₹)",
)