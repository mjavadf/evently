from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from events import serializers
from events.serializers import EventSerializer, EventListSerializer
from .models import Event


@api_view(["GET"])
def home(request):
    events = Event.objects.all().order_by("id")
    serializer = EventListSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    serializer = EventSerializer(event)
    return Response(serializer.data)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_classes = {"list": EventListSerializer}
    default_serializer_class = EventSerializer
    
    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)
