from rest_framework import serializers
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
        event_id = self.context["event_id"]
        return Ticket.objects.create(event_id=event_id, **validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'birth_date', 'bio', 'location', 'website']