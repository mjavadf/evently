from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Event, Profile, Ticket


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer",
            "category",
            "tickets",
        )

    tickets = serializers.SerializerMethodField()

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title", "date", "location", "price", "organizer")

    price = serializers.SerializerMethodField(method_name="price_calculator")

    def price_calculator(self, event: Event):
        tickets = event.tickets.all()
        if tickets.count() > 1:
            prices = [ticket.price for ticket in tickets]
            min_price = "Free" if min(prices) == 0 else min(prices)
            return f"{min_price} - {max(prices)}"
        elif tickets.count() == 1:
            return "Free" if tickets[0].price == 0 else tickets[0].price
        else:
            return "Free"


class TicketSerializer(serializers.ModelSerializer):
    purchased = serializers.IntegerField(read_only=True)
    available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "price",
            "capacity",
            "purchased",
            "available",
            "description",
        )

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context["event_pk"])
        if event.organizer != self.context["user"]:
            raise PermissionDenied("You are not the organizer of this event")
        ticket = Ticket.objects.create(event=event, **validated_data)
        return ticket


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user_id", "birth_date", "bio", "location", "website"]
