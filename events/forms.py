from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["description", "price", "available_tickets"]


class BookingForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Number of tickets",
    )