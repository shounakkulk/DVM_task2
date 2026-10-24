
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from accounts.models import Organization
from .models import Event
from .forms import EventForm


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

    if organization is None:
        return HttpResponseForbidden(
            "You do not have permission to manage events."
        )

    events = Event.objects.filter(organization=organization)

    return render(
        request,
        "events/event_list.html",
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
            return redirect("event_list")
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
            return redirect("event_list")
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
        return redirect("event_list")

    return render(
        request,
        "events/event_confirm_delete.html",
        {"event": event},
    )
