from django.contrib import admin
from home.models import Hotel,Location,Promotions,Room,Customer,Booking,BookingRoom,Taxes,Payments,Review,Amenity,HotelImages


# Register your models here.

admin.site.register(Hotel)
admin.site.register(HotelImages)
admin.site.register(Location)
admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Taxes)
admin.site.register(Payments)
admin.site.register(BookingRoom)
admin.site.register(Review)