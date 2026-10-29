from django import forms
from django.forms import formset_factory
from .models import Event, EventSlot



class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "description",
            "event_type",
            "price",
            "available_tickets",
        ]
        labels = {
            "description": "Event Name / Description",
            "event_type": "Booking Type",
            "price": "Price per ticket / place (₹)",
            "available_tickets": "Total Available Tickets",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        event_type = None

        if self.is_bound:
            event_type = self.data.get("event_type")
        elif self.instance and self.instance.pk:
            event_type = self.instance.event_type

        if event_type == Event.SLOT:
            self.fields.pop("available_tickets")

class BookingForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Number of tickets / places",
    )


class EventSlotForm(forms.ModelForm):
    class Meta:
        model = EventSlot
        fields = ["start_time", "end_time", "capacity"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
        labels = {
            "start_time": "Slot start time",
            "end_time": "Slot end time",
            "capacity": "Maximum bookings for this slot",
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "end_time",
                "The end time must be after the start time.",
            )

        return cleaned_data


EventSlotFormSet = formset_factory(
    EventSlotForm,
    extra=1,
    can_delete=True,
)