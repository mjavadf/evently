from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from events.permissions import IsOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    EventDetailSerialzier,
    # EventImageSerializer,
    EventSerializer,
    EventListSerializer,
    LocationSerializer,
    ProfileSerializer,
    TicketSerializer,
    ReservationSerializer,
    ReservationCreateSerializer,
)
from rest_framework.generics import ListCreateAPIView, ListAPIView
from .models import Category, Event, Location, Profile, Ticket, Reservation
from .permissions import IsAdminOrIsSelf
from .mixins import CheckParentPermissionMixin


class EventViewSet(ModelViewSet):
    queryset = Event.objects.prefetch_related("tickets", "location").all().order_by("-id")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "organizer"]
    # permission_classes = [IsOwnerOrReadOnly]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return EventListSerializer
        elif self.action in ["retrieve"]:
            return EventDetailSerialzier
        else:
            return EventSerializer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        events = Event.objects.filter(organizer=request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)


class TicketViewSet(CheckParentPermissionMixin, ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsOwnerOrReadOnly]

    parent_queryset = Event.objects.all()
    parent_lookup_field = "id"
    parent_lookup_url_kwarg = "event_pk"
    lookup_field = "id"

    def get_queryset(self):
        return Ticket.objects.filter(event_id=self.kwargs["event_pk"]).order_by("id")

    def get_serializer_context(self):
        return {"event_pk": self.kwargs["event_pk"], "user": self.request.user}


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminOrIsSelf]
    queryset = Profile.objects.prefetch_related("user").all()
    lookup_field = "user__username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    @action(detail=False, methods=["get", "put"], permission_classes=[IsAuthenticated])
    def me(self, request):
        profile = Profile.objects.get(user=request.user)
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # users that aren't admin can't see the list of profiles
    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().list(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "You don't have permission to view the profiles."},
                status=403,
            )
            
    @action(detail=True, methods=["delete"], permission_classes=[IsAdminOrIsSelf])
    def remove_image(self, request, user__username=None):
        profile = self.get_object()
        if profile.image:
            profile.image.delete()  # Remove the image file
            profile.image = None    # Clear the image field in the model
            profile.save()
            return Response({"detail": "Profile image removed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No profile image to remove"}, status=status.HTTP_204_NO_CONTENT)


class ReservationViewSet(ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.all()
        else:
            return Reservation.objects.filter(participant=self.request.user)

    def get_serializer_class(self):
        # ReservationSerializer for list action and ReservationCreateSerializer for create action
        if self.request.method == "GET":
            return ReservationSerializer
        else:
            return ReservationCreateSerializer

    def get_serializer_context(self):
        return {"participant": self.request.user, "request": self.request}


# class EventImageViewSet(ModelViewSet):
#     serializer_class = EventImageSerializer

#     def get_queryset(self):
#         return EventImage.objects.filter(event_id=self.kwargs["event_pk"])

#     def get_serializer_context(self):
#         return {"event_id": self.kwargs["event_pk"], "request": self.request}


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []
    
    
class LocationListView(ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = []
    pagination_class = None