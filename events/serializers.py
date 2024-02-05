from django.urls import reverse
from rest_framework import serializers
from .models import Event, Profile, Ticket, Reservation, Location, EventImage


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "name", "country", "city", "address", "latitude", "longitude")
        

class EventImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        event_id = self.context["event_id"]
        return EventImage.objects.create(event_id=event_id, **validated_data)
    
    class Meta:
        model = EventImage
        fields = ("id", "image")


class EventSerializer(serializers.ModelSerializer):
    tickets = serializers.SerializerMethodField()
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', required=False, allow_null=True
    )
    location = LocationSerializer(required=False)
    images = EventImageSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "end_date",
            "organizer",
            "category",
            "tickets",
            "location_id",
            "location",
            "images"
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
    images = EventImageSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = ("id", "title", "date", "end_date", "price", "organizer", "location", "images")

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
            "needs_approval",
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
            "image",
            "location",
            "website",
        ]

    def get_absolute_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(
            reverse("profiles-detail", args=[obj.user.username])
        )


class ReservationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    payment_amount = serializers.DecimalField(
        read_only=True, max_digits=6, decimal_places=2
    )
    code = serializers.IntegerField(read_only=True)
    qrcode = serializers.ImageField(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "ticket",
            "participant",
            "status",
            "payment_status",
            "payment_amount",
            "payment_method",
            "code",
            "qrcode",
        )


class ReservationCreateSerializer(serializers.ModelSerializer):
    ticket_id = serializers.IntegerField()
    status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    code = serializers.IntegerField(read_only=True)
    qrcode = serializers.ImageField(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "ticket_id",
            "status",
            "payment_status",
            "payment_method",
            "code",
            "qrcode",
        )

    def create(self, validated_data):
        ticket = Ticket.objects.get(id=validated_data["ticket_id"])
        participant = self.context["participant"]
        payment_amount = ticket.price
        need_approval = ticket.needs_approval
        # Check if user has reserved this event before, prevent duplicate resrvations
        if Reservation.objects.filter(ticket=ticket, participant=participant).exists():
            raise serializers.ValidationError(
                "You have already made a reservation for this event"
            )
        (is_successful, availablity_type) = ticket.buy()
        if is_successful and availablity_type == "available" :
            return Reservation.objects.create(
                participant=participant, payment_amount=payment_amount, **validated_data, status="A" if not need_approval else "P"
            )
        elif is_successful and availablity_type == "waitlist":
            return Reservation.objects.create(
                participant=participant, payment_amount=payment_amount, **validated_data, status="W"
            )
        raise serializers.ValidationError("Ticket is not available")
