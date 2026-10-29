from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Organization


from django.contrib import messages
from django.db import transaction
from django.db.models import F


from .forms import AddMoneyForm
from .models import Organization, Wallet, Transaction

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda user: user.is_superuser)
def create_organization_account(request):
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

            messages.success(
                request,
                "Organization account created successfully!",
            )
            return redirect("home")

        if not organization_name:
            form.add_error(
                None,
                "Organization name is required.",
            )
    else:
        form = UserCreationForm()

    return render(
        request,
        "accounts/create_organization_account.html",
        {"form": form},
    )

def is_ordinary_user(user):
    return (
        user.is_authenticated
        and not user.groups.filter(name="Organizations").exists()
    )


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

@login_required
def home(request):
    if request.user.is_superuser:
        return redirect("superuser_dashboard")

    if request.user.groups.filter(
        name="Organizations"
    ).exists():
        return redirect("organization_dashboard")

    return render(request, "accounts/home.html")


@login_required
def superuser_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "You do not have permission to access this page."
        )

    return render(
        request,
        "accounts/superuser_dashboard.html",
    )

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
@login_required
def add_money(request):
    if not is_ordinary_user(request.user):
            return HttpResponseForbidden(
                "Only ordinary users can access the wallet."
            )
    if request.method == "POST":
        form = AddMoneyForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]

            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(
                    user=request.user
                )

                Wallet.objects.filter(pk=wallet.pk).update(
                    balance=F("balance") + amount
                )

                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type=Transaction.DEPOSIT,
                    amount=amount,
                    description="Added money to wallet",
                )

            messages.success(
                request,
                f"₹{amount} added to your wallet successfully!",
            )
            return redirect("home")
    else:
        form = AddMoneyForm()

    return render(
        request,
        "accounts/add_money.html",
        {"form": form},
    )
@login_required
def transaction_history(request):
    if not is_ordinary_user(request.user):
        return HttpResponseForbidden(
            "Only ordinary users can access the wallet."
        )
    wallet, created = Wallet.objects.get_or_create(
        user=request.user
    )

    transactions = wallet.transactions.order_by("-created_at")

    return render(
        request,
        "accounts/transaction_history.html",
        {"transactions": transactions},
    )

@login_required
def wallet_balance(request):
    if not is_ordinary_user(request.user):
            return HttpResponseForbidden(
                "Only ordinary users can access the wallet."
            )
    wallet, created = Wallet.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "accounts/wallet_balance.html",
        {"wallet": wallet},
    )
