from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("events", views.EventViewSet)
urlpatterns = router.urls

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('event/<int:id>/', views.event_detail, name='event_detail'),
# ]
