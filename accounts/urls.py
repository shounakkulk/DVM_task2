
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from events.views import my_bookings


urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "register/organization/",
        views.register_organization,
        name="register_organization",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "add-money/", 
        views.add_money, 
        name="add_money",
    ),
    path(
        "transactions/",
        views.transaction_history,
        name="transaction_history",
    ),
    path(
        "wallet-balance/",
        views.wallet_balance,
        name="wallet_balance",
    ),
    path(
        "my-bookings/",
        my_bookings,
        name="my_bookings",
    ),
]
