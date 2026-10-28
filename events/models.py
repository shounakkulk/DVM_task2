from django.db import models
from accounts.models import Organization
from django.conf import settings


class Event(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="events",
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.PositiveIntegerField()

    def __str__(self):
        return self.description[:50]

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
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.event.description[:30]} "
            f"(x{self.quantity})"
        )