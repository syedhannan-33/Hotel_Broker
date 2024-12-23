from django.contrib import admin
from django.urls import path, include  # Add include here

admin.site.site_header = "Hotel Admin"
admin.site.site_title = "Hotel Admin Portal"
admin.site.index_title = "Welcome to Hotel Admin Portal"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Now include will work
]
