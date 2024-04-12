from django.urls import reverse
from rest_framework import serializers
from .models import Category, Event, Profile, Ticket, Reservation, Location
from .utils import calendar_link_generator
from core.serializers import CustomUserDetailSerialzier


class LocationSerializer(serializers.ModelSerializer):
    # "country", "city", "address" accept null values
    country = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    class Meta:
        model = Location
        fields = ("id", "country", "city", "address", "latitude", "longitude")


# class EventImageSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         event_id = self.context["event_id"]
#         return EventImage.objects.create(event_id=event_id, **validated_data)

#     class Meta:
#         model = EventImage
#         fields = ("id", "image")

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class EventDetailSerialzier(serializers.ModelSerializer):
    tickets = serializers.SerializerMethodField()
    organizer = CustomUserDetailSerialzier(read_only=True)
    category = CategorySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    # images = EventImageSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "end_date",
            "cover",
            "organizer",
            "category",
            "location_type",
            "meeting_link",
            "location",
            "tickets",
        )

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data

class EventSerializer(serializers.ModelSerializer):
    organizer = CustomUserDetailSerialzier(read_only=True)
    # images = EventImageSerializer(many=True, required=False)
    location = LocationSerializer(required=False)
    

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
            "cover",
            "location_type",
            "meeting_link",
            "location",
        )

    def get_tickets(self, obj):
        return TicketSerializer(obj.tickets.all(), many=True).data

    def create(self, validated_data):
        organizer = self.context["request"].user
        try:
            location_details = validated_data.pop("location")
            location = Location.objects.create(**location_details)
        except KeyError:
            location = None

        event = Event.objects.create(
            organizer=organizer, location=location ,**validated_data
        )
        return event


class EventListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name="price_calculator")
    location = LocationSerializer()
    # images = EventImageSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "date",
            "end_date",
            "price",
            "organizer",
            "location_type",
            "meeting_link",
            "location",
            "cover",
        )

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
    add_to_calendar = serializers.SerializerMethodField(
        method_name="calendar_link", read_only=True
    )

    def calendar_link(self, reservation: Reservation):
        return calendar_link_generator(reservation)

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
            "add_to_calendar",
        )


class ReservationCreateSerializer(serializers.ModelSerializer):
    ticket_id = serializers.IntegerField()
    status = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(read_only=True)
    code = serializers.IntegerField(read_only=True)
    qrcode = serializers.ImageField(read_only=True)
    add_to_calendar = serializers.SerializerMethodField(
        method_name="calendar_link", read_only=True
    )

    def calendar_link(self, reservation: Reservation):
        return calendar_link_generator(reservation)

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
            "add_to_calendar",
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
        if is_successful and availablity_type == "available":
            return Reservation.objects.create(
                participant=participant,
                payment_amount=payment_amount,
                **validated_data,
                status="A" if not need_approval else "P",
            )
        elif is_successful and availablity_type == "waitlist":
            return Reservation.objects.create(
                participant=participant,
                payment_amount=payment_amount,
                **validated_data,
                status="W",
            )
        raise serializers.ValidationError("Ticket is not available")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
