from django.contrib import messages
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from accounts.models import Organization, Wallet, Transaction as WalletTransaction
from django.db import models, transaction
from .models import Event, EventSlot, Booking
from .forms import EventForm, BookingForm, EventSlotFormSet
from django.utils import timezone

from django.contrib.auth.decorators import login_required

def get_user_organization(user):
    if not user.groups.filter(name="Organizations").exists():
        return None

    try:
        return user.organization
    except Organization.DoesNotExist:
        return None


@login_required
def event_list(request):
    organization = get_user_organization(request.user)

    if organization is not None:
        events = Event.objects.filter(organization=organization)
    else:
        events = Event.objects.all()

    for event in events:
        if event.event_type == Event.SLOT:
            event.display_slots = event.slots.annotate(
                booked_places=Sum("bookings__quantity")
            )

            for slot in event.display_slots:
                slot.remaining_capacity = (
                    slot.capacity - (slot.booked_places or 0)
                )

    return render(
        request,
        "events/event_list.html",
        {"events": events},
    )
@login_required
def my_events(request):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to manage events."
        )

    events = Event.objects.filter(
        organization=organization
    ).prefetch_related("slots__bookings")

    for event in events:
        if event.event_type == Event.SLOT:
            for slot in event.slots.all():
                slot.booked_places = sum(
                    booking.quantity for booking in slot.bookings.all()
                )
                slot.remaining_capacity = max(
                    0, slot.capacity - slot.booked_places
                )

    return render(
        request,
        "events/my_events.html",
        {"events": events},
    )

@login_required
def event_create(request):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to create events."
        )

    if request.method == "POST":
        form = EventForm(request.POST)
        slot_formset = EventSlotFormSet(
            request.POST,
            prefix="slots",
        )

        if form.is_valid():
            event_type = form.cleaned_data["event_type"]

            if event_type == Event.SLOT:
                if not slot_formset.is_valid():
                    return render(
                        request,
                        "events/event_create.html",
                        {
                            "form": form,
                            "slot_formset": slot_formset,
                        },
                    )

                valid_slots = [
                    slot_form.cleaned_data
                    for slot_form in slot_formset
                    if slot_form.cleaned_data
                    and not slot_form.cleaned_data.get("DELETE", False)
                ]

                if not valid_slots:
                    slot_formset.forms[0].add_error(
                        None,
                        "Add at least one valid slot.",
                    )
                    return render(
                        request,
                        "events/event_create.html",
                        {
                            "form": form,
                            "slot_formset": slot_formset,
                        },
                    )

            with transaction.atomic():
                event = form.save(commit=False)
                event.organization = organization

                if event_type == Event.SLOT:
                    event.available_tickets = 0

                event.save()

                if event_type == Event.SLOT:
                    for slot_data in valid_slots:
                        EventSlot.objects.create(
                            event=event,
                            start_time=slot_data["start_time"],
                            end_time=slot_data["end_time"],
                            capacity=slot_data["capacity"],
                        )

            messages.success(request, "Event created successfully!")
            return redirect("my_events")

    else:
        form = EventForm()
        slot_formset = EventSlotFormSet(prefix="slots")

    return render(
        request,
        "events/event_create.html",
        {
            "form": form,
            "slot_formset": slot_formset,
        },
    )

@login_required
def event_edit(request, event_id):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to edit events."
        )

    event = get_object_or_404(
        Event,
        id=event_id,
        organization=organization,
    )

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
            return redirect("my_events")
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "events/event_edit.html",
        {"form": form, "event": event},
    )


@login_required
def event_delete(request, event_id):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to delete events."
        )

    event = get_object_or_404(
        Event,
        id=event_id,
        organization=organization,
    )

    if request.method == "POST":
        event.delete()
        return redirect("my_events")

    return render(
        request,
        "events/event_confirm_delete.html",
        {"event": event},
    )


@login_required
def book_event(request, event_id):
    if request.user.groups.filter(name="Organizations").exists():
        return HttpResponseForbidden(
            "Organization accounts cannot book events."
        )

    event = get_object_or_404(Event, id=event_id)

    slots = EventSlot.objects.filter(event=event).order_by("start_time")

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            slot_id = request.POST.get("slot")

            with transaction.atomic():
                event = Event.objects.select_for_update().get(id=event_id)

                slot = None

                if event.event_type == Event.SLOT:
                    if not slot_id:
                        form.add_error(None, "Please select a slot.")
                    else:
                        slot = EventSlot.objects.select_for_update().filter(
                            id=slot_id,
                            event=event,
                        ).first()

                        if slot is None:
                            form.add_error(None, "Please select a valid slot.")
                        else:
                            already_booked = Booking.objects.filter(
                                slot=slot
                            ).aggregate(
                                total=models.Sum("quantity")
                            )["total"] or 0

                            if quantity > slot.capacity - already_booked:
                                form.add_error(
                                    "quantity",
                                    "Not enough places remain in this slot.",
                                )

                elif quantity > event.available_tickets:
                    form.add_error(
                        "quantity",
                        "Not enough tickets are available.",
                    )

                if not form.errors:
                    wallet, created = Wallet.objects.get_or_create(
                        user=request.user
                    )
                    wallet = Wallet.objects.select_for_update().get(
                        id=wallet.id
                    )

                    total_price = event.price * quantity

                    if wallet.balance < total_price:
                        form.add_error(
                            None,
                            "Insufficient wallet balance. Please add money.",
                        )
                    else:
                        Wallet.objects.filter(pk=wallet.pk).update(
                            balance=F("balance") - total_price
                        )

                        if event.event_type == Event.TICKET:
                            Event.objects.filter(pk=event.pk).update(
                                available_tickets=(
                                    F("available_tickets") - quantity
                                )
                            )

                        Booking.objects.create(
                            user=request.user,
                            event=event,
                            slot=slot,
                            quantity=quantity,
                            total_price=total_price,
                        )

                        WalletTransaction.objects.create(
                            wallet=wallet,
                            transaction_type=WalletTransaction.BOOKING,
                            amount=total_price,
                            description=(
                                f"Booked {quantity} place(s) for "
                                f"{event.description[:150]}"
                            ),
                        )

                        messages.success(
                            request,
                            f"Successfully booked {quantity} place(s) "
                            f"for ₹{total_price}.",
                        )
                        return redirect("event_list")

    else:
        form = BookingForm()

    return render(
        request,
        "events/book_event.html",
        {
            "event": event,
            "form": form,
            "slots": slots,
        },
    )
@login_required
def my_bookings(request):
    if request.user.groups.filter(name="Organizations").exists():
        return HttpResponseForbidden(
            "Organization accounts cannot view user bookings."
        )

    bookings = Booking.objects.filter(
        user=request.user
    ).select_related("event").order_by("-created_at")

    return render(
        request,
        "events/my_bookings.html",
        {"bookings": bookings},
    )

@login_required
def organization_bookings(request):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to view organization bookings."
        )

    bookings = Booking.objects.filter(
        event__organization=organization
    ).select_related(
        "user",
        "event",
        "slot",
    ).order_by("-created_at")

    return render(
        request,
        "events/organization_bookings.html",
        {"bookings": bookings},
    )

@login_required
def mark_booking_consumed(request, booking_id):
    if request.method != "POST":
        return HttpResponseForbidden(
            "This action requires a POST request."
        )

    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to consume tickets."
        )

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        event__organization=organization,
    )

    if booking.is_consumed:
        messages.info(request, "This booking has already been consumed.")
    else:
        booking.is_consumed = True
        booking.consumed_at = timezone.now()
        booking.save(update_fields=["is_consumed", "consumed_at"])

        messages.success(
            request,
            f"Booking #{booking.id} marked as consumed.",
        )

    return redirect("organization_bookings")

@login_required
def organization_analytics(request):
    organization = get_user_organization(request.user)

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to view analytics."
        )

    events = Event.objects.filter(
        organization=organization
    ).prefetch_related("slots")

    bookings = Booking.objects.filter(
        event__organization=organization
    )

    summary = bookings.aggregate(
        total_revenue=Sum("total_price"),
        total_places_booked=Sum("quantity"),
    )

    total_events = events.count()
    total_bookings = bookings.count()
    total_revenue = summary["total_revenue"] or 0
    total_places_booked = summary["total_places_booked"] or 0

    consumed_bookings = bookings.filter(is_consumed=True).count()
    pending_bookings = bookings.filter(is_consumed=False).count()

    for event in events:
        event.total_bookings = event.bookings.count()
        event.places_booked = (
            event.bookings.aggregate(total=Sum("quantity"))["total"] or 0
        )
        event.booking_revenue = (
            event.bookings.aggregate(total=Sum("total_price"))["total"] or 0
        )

        if event.event_type == Event.TICKET:
            event.remaining_inventory = event.available_tickets

        else:
            for slot in event.slots.all():
                slot.places_booked = (
                    slot.bookings.aggregate(total=Sum("quantity"))["total"] or 0
                )
                slot.remaining_capacity = max(
                    0, slot.capacity - slot.places_booked
                )

    context = {
        "total_events": total_events,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "total_places_booked": total_places_booked,
        "consumed_bookings": consumed_bookings,
        "pending_bookings": pending_bookings,
        "events": events,
    }

    return render(
        request,
        "events/organization_analytics.html",
        context,
    )