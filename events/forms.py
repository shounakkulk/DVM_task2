from django import forms
from django.forms import formset_factory, inlineformset_factory
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
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["start_time"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]
        self.fields["end_time"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]


EventSlotFormSet = inlineformset_factory(
    Event,
    EventSlot,
    form=EventSlotForm,
    extra=0,
    can_delete=True,
)