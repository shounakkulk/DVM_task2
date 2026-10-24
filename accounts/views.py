
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Organization


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            group, created = Group.objects.get_or_create(
                name="Users"
            )
            user.groups.add(group)

            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def register_organization(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        organization_name = request.POST.get(
            "organization_name", ""
        ).strip()

        if form.is_valid() and organization_name:
            user = form.save()

            group, created = Group.objects.get_or_create(
                name="Organizations"
            )
            user.groups.add(group)

            Organization.objects.create(
                user=user,
                name=organization_name,
            )

            login(request, user)
            return redirect("organization_dashboard")
    else:
        form = UserCreationForm()

    return render(
        request,
        "accounts/register_organization.html",
        {"form": form},
    )


@login_required
def home(request):
    if request.user.groups.filter(
        name="Organizations"
    ).exists():
        return redirect("organization_dashboard")

    return render(request, "accounts/home.html")


@login_required
def organization_dashboard(request):
    if not request.user.groups.filter(
        name="Organizations"
    ).exists():
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    try:
        organization = request.user.organization
    except Organization.DoesNotExist:
        return HttpResponseForbidden(
            "This account does not have an organization profile."
        )

    return render(
        request,
        "accounts/organization_dashboard.html",
        {"organization": organization},
    )
