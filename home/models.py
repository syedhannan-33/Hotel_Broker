from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator , MaxValueValidator
from django.core.exceptions import ValidationError


# Create your models here.
class Customer(models.Model):
    """Customer Model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    phone = models.CharField(max_length=20, blank=False, null=False,unique=True)
    address = models.CharField(max_length=255, blank=False, null=False)
    is_blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Blacklisted' if self.is_blacklisted else 'Active'}"

class Taxes(models.Model):
    """Taxation Class"""

    percentage  =   models.PositiveSmallIntegerField()
    description =   models.CharField(max_length=100)

    def __str__(self):
        return f"{self.description} - {self.percentage}%"

class Amenity(models.Model):
    """Model for an amenity in a hotel or room (e.g., Wi-Fi, Pool, Gym)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # Optional description of the amenity

    def __str__(self):
        return self.name

# location = models.ForeignKey('home.Location', on_delete=models.CASCADE)

class Location(models.Model):
    """Location Model"""
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    country         = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"


class Hotel(models.Model):
    """Hotel Model"""
    location = models.ForeignKey('home.Location', on_delete=models.CASCADE)

    name            = models.CharField(max_length=100 , unique=True)
    stars           = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    is_suspended    = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)
    room_count      = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.stars} Stars"

    def save(self, *args, **kwargs):
        """Override save to create rooms automatically."""
        is_new = self.pk is None  # Check if it's a new hotel instance
        super().save(*args, **kwargs)  # Save the hotel first

        if is_new and self.room_count > 0:
            # Create rooms only if the hotel is new and room_count > 0
            self.create_rooms(self.room_count)

    def create_rooms(self, room_count):
        """Create rooms for the hotel when it's created."""
        for i in range(1, room_count + 1):
            # Create a new room instance for each room
            Room.objects.create(
                hotel=self,
                room_number=i,
                is_Booked=False,
                type=Room.RoomType.STANDARD,  # You can customize room types
                price_per_night=Decimal('1250.00')  # You can set a default price or modify this
            )


class HotelImages(models.Model):
    hotel= models.ForeignKey(Hotel ,related_name="images", on_delete=models.CASCADE)
    images = models.ImageField(upload_to="hotels")

    def __str__(self):
            return f"Image for {self.hotel.name} - {self.images.name.split('/')[-1]}"

class HotelBooking(models.Model):
    hotel= models.ForeignKey(Hotel  , related_name="hotel_bookings" , on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name="user_bookings" , on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    booking_type= models.CharField(max_length=100,choices=(('Pre Paid' , 'Pre Paid') , ('Post Paid' , 'Post Paid')))

    def __str__(self) -> str:
        return f'{self.hotel.hotel_name} {self.start_date} to {self.end_date}'

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


class Room(models.Model):
    """Room Model"""
    class RoomType(models.TextChoices):
        STANDARD = 'Standard'
        SUPERIOR = 'Superior'
        DELUXE = 'Deluxe'
        SUITE = 'Suite'
        FAMILY = 'Family'

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    amenities = models.ManyToManyField(Amenity, related_name='room', blank=True)  # Many-to-many relation to Amenity

    room_number = models.IntegerField(default=0)
    is_Booked = models.BooleanField(default=False)
    type = models.CharField(max_length=100, choices=RoomType.choices)
    price_per_night = models.DecimalField(decimal_places=2, max_digits=10 ,  validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"Room {self.room_number} ({self.type}) - {self.hotel.name}"




class Booking(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        COMPLETED = 'Completed'
        CANCELED = 'Canceled'

    """Booking Model"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room,on_delete=models.CASCADE , related_name='bookings')
    tax  = models.ForeignKey(Taxes,on_delete=models.CASCADE,related_name='bookings')

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

    booking = models.ForeignKey(Booking,on_delete=models.CASCADE , related_name='payments')

    date    = models.DateTimeField()
    Amount  = models.DecimalField(max_digits=10, decimal_places=2 ,  validators=[MinValueValidator(Decimal('0.01'))])
    method  = models.CharField(max_length=100 , choices=MethodChoice.choices)
    Status  = models.CharField(max_length=100 , choices=StatusChoice.choices)

    def __str__(self):
        return f"Payment of {self.Amount} ({self.method}) - {self.booking} [{self.Status}]"

    def calculate_amount(self):
        """Calculate the payment amount based on room price, nights, and tax."""
        if not self.booking or not self.booking.room or not self.booking.tax:
            raise ValueError("Booking, room, or tax information is missing.")

        # Get the price per night and the number of nights
        price_per_night = self.booking.room.price_per_night
        nights = (self.booking.end_date - self.booking.start_date).days

        # Calculate the base amount (price per night * number of nights)
        base_amount = price_per_night * nights

        # Get the tax percentage and apply it to the base amount
        tax_percentage = self.booking.tax.percentage
        tax_amount = (base_amount * tax_percentage) / Decimal('100')

        # Final amount includes base amount + tax
        final_amount = base_amount + tax_amount
        return final_amount

    def save(self, *args, **kwargs):
        """Override save method to calculate the amount before saving."""
        # Calculate and set the amount before saving the payment instance
        if self.Amount is None:  # Calculate amount only if not already set
            self.Amount = self.calculate_amount()
        super().save(*args, **kwargs)

class Review(models.Model):
    """Model Class"""

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE , related_name='review')
    hotel   = models.ForeignKey(Hotel , on_delete=models.CASCADE , related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    description = models.TextField(blank=True , null=True)
    date = models.DateField()
