from django.urls import reverse
from rest_framework import serializers
from .models import Event, Profile, Ticket, Registration, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "name", "country", "city", "address", "latitude", "longitude")


class EventSerializer(serializers.ModelSerializer):
    tickets = serializers.SerializerMethodField()
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', required=False, allow_null=True
    )
    location = LocationSerializer(required=False)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "organizer",
            "category",
            "tickets",
            "location_id",
            "location",
        )

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data

    def create(self, validated_data):
        organizer = self.context["request"].user
        
        location_data = validated_data.pop('location', None)
        location_id = validated_data.pop('location_id', None)

        if location_id:
            location = Location.objects.get(id=location_id)
        elif location_data:
            location = Location.objects.create(**location_data)
        else:
            location = None

        event = Event.objects.create(organizer=organizer, location=location, **validated_data)
        return event
    
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        location_id = validated_data.pop('location_id', None)

        if location_id:
            location = Location.objects.get(id=location_id)
        elif location_data:
            location = Location.objects.create(**location_data)
        else:
            location = None

        instance.location = location
        instance.save()

        return super().update(instance, validated_data)


class EventListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name="price_calculator")
    location = LocationSerializer()

    class Meta:
        model = Event
        fields = ("id", "title", "date", "price", "organizer", "location")

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
        return request.build_absolute_uri(
            reverse("profiles-detail", args=[obj.user.username])
        )


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
