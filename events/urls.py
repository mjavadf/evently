from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("events", views.EventViewSet)
router.register("profiles", views.ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("events/<int:event_id>/tickets/", views.TicketList.as_view()),
]
