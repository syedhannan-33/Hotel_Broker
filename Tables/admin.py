from django.contrib import admin
from Tables.models import Hotel,Location,Promotions,Room,Customer,Booking,BookingRoom,Taxes,Payments

# Register your models here.

admin.site.register(Hotel)
admin.site.register(Location)
admin.site.register(Promotions)
admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Taxes)
admin.site.register(Payments)
admin.site.register(BookingRoom)