
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("events", views.EventViewSet, basename="events")
router.register("profiles", views.ProfileViewSet, basename="profiles")

events_router = routers.NestedDefaultRouter(router, "events", lookup="event")
events_router.register("tickets", views.TicketViewSet, basename="tickets")

urlpatterns = router.urls + events_router.urls