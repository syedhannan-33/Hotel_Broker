from django.contrib import admin
from Tables.models import Hotel,Location,Promotions,Room,Customer,Booking

# Register your models here.

admin.site.register(Hotel)
admin.site.register(Location)
admin.site.register(Promotions)
admin.site.register(Room)
admin.site.register(Customer)
admin.site.register(Booking)