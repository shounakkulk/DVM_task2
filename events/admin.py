from django.contrib import admin
from .models import Event, Booking, EventSlot

admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(EventSlot)