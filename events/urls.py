from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("events", views.EventViewSet, basename="events")
router.register("profiles", views.ProfileViewSet, basename="profiles")
router.register("reservations", views.ReservationViewSet, basename="reservations")

events_router = routers.NestedDefaultRouter(router, "events", lookup="event")
events_router.register("tickets", views.TicketViewSet, basename="tickets")
# events_router.register("images", views.EventImageViewSet, basename="images")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(events_router.urls)),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
]
