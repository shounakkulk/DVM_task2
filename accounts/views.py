from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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
        {"form": form}
    )

@login_required
def home(request):
    return render(request, "accounts/home.html")

@login_required
def organization_dashboard(request):
    if not request.user.groups.filter(name="Organizations").exists():
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    if not hasattr(request.user, "organization"):
        return HttpResponseForbidden(
            "This account does not have an organization profile."
        )

    return render(
        request,
        "accounts/organization_dashboard.html",
        {"organization": request.user.organization},
    )