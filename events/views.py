
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from accounts.models import Organization
from .models import Event
from .forms import EventForm


@login_required
def event_list(request):
    if not request.user.groups.filter(name="Organizations").exists():
        return HttpResponseForbidden(
            "You do not have permission to manage events."
        )

    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        return HttpResponseForbidden(
            "This account has no organization profile."
        )

    events = Event.objects.filter(organization=organization)

    return render(
        request,
        "events/event_list.html",
        {"events": events},
    )


@login_required
def event_create(request):
    if not request.user.groups.filter(name="Organizations").exists():
        return HttpResponseForbidden(
            "You do not have permission to create events."
        )

    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        return HttpResponseForbidden(
            "This account has no organization profile."
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
