from django.urls import reverse
from rest_framework import serializers
from .models import Event, Profile, Ticket, Registration


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
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data

    def create(self, validated_data):
        organizer = self.context["request"].user
        return Event.objects.create(organizer=organizer, **validated_data)


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
        # if event.organizer != self.context["user"]:
        #     raise PermissionDenied("You are not the organizer of this event")
        ticket = Ticket.objects.create(event=event, **validated_data)
        return ticket


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True, source="user.username")
    # use models get_absolute_url method to get the url
    profile_url = serializers.SerializerMethodField(method_name="get_absolute_url")

    class Meta:
        model = Profile
        fields = [
            "id",
            "user_id",
            "username",
            "profile_url",
            "birth_date",
            "bio",
            "location",
            "website",
        ]
        
    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(reverse("profiles-detail", args=[obj.user.username]))
    


class RegistrationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    payment_amount = serializers.DecimalField(
        read_only=True, max_digits=6, decimal_places=2
    )

    class Meta:
        model = Registration
        fields = (
            "id",
            "ticket",
            "participant",
            "status",
            "payment_status",
            "payment_amount",
            "payment_method",
        )


class RegistrationCreateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Registration
        fields = (
            "id",
            "ticket",
            "status",
            "payment_status",
            "payment_method",
        )

    def create(self, validated_data):
        ticket = validated_data["ticket"]
        participant = self.context["participant"]
        payment_amount = ticket.price
        # Check if user has registered for this event before, prevent duplicate registration
        if Registration.objects.filter(ticket=ticket, participant=participant).exists():
            raise serializers.ValidationError(
                "You have already registered for this event"
            )
        if ticket.buy():
            return Registration.objects.create(
                participant=participant, payment_amount=payment_amount, **validated_data
            )
        raise serializers.ValidationError("Ticket is not available")
