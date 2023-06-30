from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register("events", views.EventViewSet)
router.register("profiles", views.ProfileViewSet)

events_router = routers.NestedDefaultRouter(router, "events", lookup="event")
events_router.register("tickets", views.TicketViewSet, basename="tickets")

urlpatterns = router.urls + events_router.urls
# urlpatterns = [
#     path('', include(router.urls)),
#     path("events/<int:event_id>/tickets/", views.TicketList.as_view()),
# ]
