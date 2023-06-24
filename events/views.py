from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView
from .serializers import EventSerializer, EventListSerializer, TicketSerializer
from .models import Event, Ticket
from events import serializers


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_classes = {"list": EventListSerializer}
    default_serializer_class = EventSerializer
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class TicketList(ListCreateAPIView):
    serializer_class = TicketSerializer
    
    def get_serializer_context(self):
        return {"event_id": self.kwargs["event_id"]}
    
    def get_queryset(self):
        return Ticket.objects.filter(event_id=self.kwargs["event_id"])