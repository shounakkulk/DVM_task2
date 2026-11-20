from django.contrib import admin
from .models import Organization, Transaction, Wallet


admin.site.register(Organization)
admin.site.register(Transaction)
admin.site.register(Wallet)