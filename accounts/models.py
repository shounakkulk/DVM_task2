from django.conf import settings
from django.db import models


class Organization(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization",
    )
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    def __str__(self):
        return f"{self.user.username}'s Wallet"

class Transaction(models.Model):
    DEPOSIT = "DEPOSIT"
    BOOKING = "BOOKING"

    TRANSACTION_TYPES = [
        (DEPOSIT, "Wallet Deposit"),
        (BOOKING, "Event Booking"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: ₹{self.amount}"