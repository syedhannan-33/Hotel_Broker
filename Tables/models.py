from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator , MaxValueValidator
from django.core.exceptions import ValidationError


# Create your models here.


class Hotel(models.Model):
    hotel_id        = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    stars           = models.IntegerField( validators=[MinValueValidator(1),MaxValueValidator(5)])
    location        = models.ForeignKey('Location' , on_delete=models.CASCADE , related_name='hotels')
    is_suspended    = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)


class Location(models.Model):
    location_id     = models.AutoField(primary_key=True)
    city            = models.CharField(max_length=100)
    state           = models.CharField(max_length=100)
    country         = models.CharField(max_length=100)

class Promotions(models.Model):
    promo_id        = models.AutoField(primary_key=True)
    hotel_id        = models.ForeignKey('Hotel' , on_delete=models.CASCADE)
    discount        = models.IntegerField(validators=[MinValueValidator(5) , MaxValueValidator(100)])
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")


class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_blacklisted = models.BooleanField(default=False)

"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders') 

    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders') 
"""





