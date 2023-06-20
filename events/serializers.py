from rest_framework import serializers


class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    date = serializers.DateTimeField()
    location = serializers.CharField(max_length=255)