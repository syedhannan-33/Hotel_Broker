
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator , MaxValueValidator
from django.core.exceptions import ValidationError


# Create your models here.


class Location(models.Model):
    """Location Model"""
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    country         = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


class Hotel(models.Model):
    """Hotel Model"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='hotels')

    name            = models.CharField(max_length=100 , unique=True)
    stars           = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    is_suspended    = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.stars} Stars"


class Promotions(models.Model):
    hotel           = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='promotions')

    discount        = models.PositiveSmallIntegerField(validators=[MinValueValidator(5) , MaxValueValidator(100)])
    start_date      = models.DateField()
    end_date        = models.DateField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

    def __str__(self):
        return f"Promotion {self.discount}% at {self.hotel.name} ({self.start_date} to {self.end_date})"

class Customer(models.Model):
    """Customer Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    phone = models.CharField(max_length=20, blank=False, null=False,unique=True)
    address = models.CharField(max_length=255, blank=False, null=False)
    is_blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Blacklisted' if self.is_blacklisted else 'Active'}"

class Room(models.Model):
    """Room Model"""
    class RoomType(models.TextChoices):
        STANDARD = 'Standard'
        SUPERIOR = 'Superior'
        DELUXE = 'Deluxe'
        SUITE = 'Suite'
        FAMILY = 'Family'

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')

    room_number = models.IntegerField(default=0)
    is_Booked = models.BooleanField(default=False)
    type = models.CharField(max_length=100, choices=RoomType.choices)
    price_per_night = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"Room {self.room_number} ({self.type}) - {self.hotel.name}"


class Taxes(models.Model):
    """Taxation Class"""

    percentage  =   models.PositiveSmallIntegerField()
    description =   models.CharField(max_length=100)

    def __str__(self):
        return f"{self.description} - {self.percentage}%"


class Booking(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        COMPLETED = 'Completed'
        CANCELED = 'Canceled'

    """Booking Model"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    tax  = models.ForeignKey(Taxes,on_delete=models.CASCADE,related_name='taxes')

    status = models.CharField(max_length=100 , choices=StatusChoices.choices)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

    def __str__(self):
        return f"Booking for {self.customer.user.username} - {self.room} ({self.status})"

class BookingRoom(models.Model):
    """Intermediate Table: Booking and Rooms"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_rooms')
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='booking_room')

    def __str__(self):
        return f"Room {self.room.room_number} in Booking #{self.booking.id}"


class Payments(models.Model):
    """Payment Class"""

    class MethodChoice(models.TextChoices):
        Cash = 'Cash'
        Card = 'Card'
        Online = 'Online'

    class StatusChoice(models.TextChoices):
        Paid    =   'Paid'
        Pending =   'Pending'

    booking = models.ForeignKey(Booking,on_delete=models.CASCADE , related_name='Payments')

    date    = models.DateTimeField()
    Amount  = models.DecimalField(max_digits=10, decimal_places=2)
    method  = models.CharField(max_length=100 , choices=MethodChoice.choices)
    Status  = models.CharField(max_length=100 , choices=StatusChoice.choices)

    def __str__(self):
        return f"Payment of {self.Amount} ({self.method}) - {self.booking} [{self.Status}]"
