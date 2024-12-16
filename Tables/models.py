
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


class Hotel(models.Model):
    """Hotel Model"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='hotels')

    name            = models.CharField(max_length=100 , unique=True)
    stars           = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    is_suspended    = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)


class Promotions(models.Model):
    hotel           = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='promotions')

    discount        = models.PositiveSmallIntegerField(validators=[MinValueValidator(5) , MaxValueValidator(100)])
    start_date      = models.DateField()
    end_date        = models.DateField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

class Customer(models.Model):
    """Customer Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    phone = models.CharField(max_length=20, blank=False, null=False,unique=True)
    address = models.CharField(max_length=255, blank=False, null=False)
    is_blacklisted = models.BooleanField(default=False)

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




class Booking(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        COMPLETED = 'Completed'
        CANCELED = 'Canceled'

    """Booking Model"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')

    status = models.CharField(max_length=100 , choices=StatusChoices.choices)
    start_date = models.DateField()
    end_date = models.DateField()



