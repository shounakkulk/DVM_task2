from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseForbidden
from accounts.models import Organization, Wallet, Transaction as WalletTransaction
from .models import Event, Booking
from .forms import EventForm, BookingForm


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
        # Organizations see only their own events.
        events = Event.objects.filter(organization=organization)
    else:
        # Ordinary users can browse all events.
        events = Event.objects.all()

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

    events = Event.objects.filter(organization=organization)

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

        if form.is_valid():
            event = form.save(commit=False)
            event.organization = organization
            event.save()
            return redirect("my_events")
    else:
        form = EventForm()

    return render(
        request,
        "events/event_create.html",
        {"form": form},
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

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            quantity = form.cleaned_data["quantity"]

            with transaction.atomic():
                event = Event.objects.select_for_update().get(
                    id=event_id
                )

                if quantity > event.available_tickets:
                    form.add_error(
                        "quantity",
                        "Not enough tickets are available.",
                    )
                else:
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
                            "Insufficient wallet balance. Please add money."
                        )
                    else:
                        Wallet.objects.filter(pk=wallet.pk).update(
                            balance=F("balance") - total_price
                        )

                        Event.objects.filter(pk=event.pk).update(
                            available_tickets=F("available_tickets") - quantity
                        )

                        Booking.objects.create(
                            user=request.user,
                            event=event,
                            quantity=quantity,
                            total_price=total_price,
                        )

                        WalletTransaction.objects.create(
                            wallet=wallet,
                            transaction_type=WalletTransaction.BOOKING,
                            amount=total_price,
                            description=(
                                f"Booked {quantity} ticket(s) "
                                f"for {event.description[:150]}"
                            ),
                        )

                        messages.success(
                            request,
                            f"Successfully booked {quantity} ticket(s) "
                            f"for ₹{total_price}",
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