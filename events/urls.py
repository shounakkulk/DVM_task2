from django.urls import path
from . import views

urlpatterns = [
    path("", views.event_list, name="event_list"),
    path("manage/", views.my_events, name="my_events"),
    path("create/", views.event_create, name="event_create"),
    path("<int:event_id>/edit/", views.event_edit, name="event_edit"),
    path("<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("<int:event_id>/book/", views.book_event,name="book_event",),
    path("my-bookings/", views.my_bookings,name="my_bookings",),
    path(
        "organization/bookings/",
        views.organization_bookings,
        name="organization_bookings",
    ),
    path(
        "organization/bookings/<int:booking_id>/consume/",
        views.mark_booking_consumed,
        name="mark_booking_consumed",
    ),
]