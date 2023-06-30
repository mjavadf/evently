from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (
    EventSerializer,
    EventListSerializer,
    ProfileSerializer,
    TicketSerializer,
)
from .models import Event, Profile, Ticket


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_classes = {"list": EventListSerializer}
    default_serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "organizer"]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(event_id=self.kwargs["event_pk"])

    def get_serializer_context(self):
        return {"event_pk": self.kwargs["event_pk"]}


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get", 'put'], permission_classes=[IsAuthenticated])
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