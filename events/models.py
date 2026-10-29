from django.db import models
from accounts.models import Organization
from django.conf import settings


class Event(models.Model):
    TICKET = "TICKET"
    SLOT = "SLOT"

    EVENT_TYPES = [
        (TICKET, "Ticket-based"),
        (SLOT, "Slot-based"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="events",
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField()

    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPES,
        default=TICKET,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:50]


class EventSlot(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="slots",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.event.description[:30]} - "
            f"{self.start_time}"
        )


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    slot = models.ForeignKey(
        EventSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_consumed = models.BooleanField(default=False)
    consumed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.event.description[:30]} "
            f"(x{self.quantity})"
        )