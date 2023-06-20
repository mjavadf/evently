from django.shortcuts import get_list_or_404, get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from events.serializers import EventSerializer
from .models import Event


@api_view(["GET"])
def home(request):
    events = get_list_or_404(Event)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)
