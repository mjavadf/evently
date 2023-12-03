from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from events.permissions import IsOwnerOfEventOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    EventSerializer,
    EventListSerializer,
    ProfileSerializer,
    TicketSerializer, RegistrationSerializer, RegistrationCreateSerializer,
)
from .models import Event, Profile, Ticket, Registration
from .permissions import IsAdminOrIsSelf
from .mixins import CheckParentPermissionMixin


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_classes = {"list": EventListSerializer}
    default_serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "organizer"]
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        events = Event.objects.filter(organizer=request.user)
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)


class TicketViewSet( CheckParentPermissionMixin, ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    parent_queryset = Event.objects.all()
    parent_lookup_field = 'id'
    parent_lookup_url_kwarg = 'event_pk'
    lookup_field = 'id'

    def get_queryset(self):
        return Ticket.objects.filter(event_id=self.kwargs["event_pk"])

    def get_serializer_context(self):
        return {"event_pk": self.kwargs["event_pk"], "user": self.request.user}


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminOrIsSelf]
    queryset = Profile.objects.all()
    lookup_field = "user__username"

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
            return Response({"detail": "You don't have permission to view the profiles."}, status=403)


class RegistrationViewSet(ModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Registration.objects.all()
        else:
            return Registration.objects.filter(participant=self.request.user)

    def get_serializer_class(self):
        # RegistrationSerializer for list action and RegistrationCreateSerializer for create action
        if self.request.method == "GET":
            return RegistrationSerializer
        else:
            return RegistrationCreateSerializer

    def get_serializer_context(self):
        return {"participant": self.request.user,
                'request': self.request}