from rest_framework import serializers
from .models import Event, Ticket


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "capacity",
            "organizer",
            "category",
            "slug",
            "tickets",
        )

    tickets = serializers.SerializerMethodField()

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title", "date", "location", "price")

    price = serializers.SerializerMethodField(method_name="price_calculator")

    def price_calculator(self, event: Event):
        tickets = event.tickets.all()
        if tickets.count() > 1:
            prices = [ticket.price for ticket in tickets]
            return f"{min(prices)} - {max(prices)}"
        elif tickets.count() == 1:
            return tickets[0].price
        else:
            return "Free"


class TicketSerializer(serializers.ModelSerializer):
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
