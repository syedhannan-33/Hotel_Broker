from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from home.models import *
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime



def check_booking(id, room_count, start_date, end_date):
    qs = HotelBooking.objects.filter(hotel__id=id)
    # qs1 = qs.filter(
    #     start_date__gte=start_date,
    #     end_date__lte=end_date,
    # )
    # qs2 = qs.filter(
    #     start_date__lte=start_date,
    #     end_date__gte=end_date,
    # )

    qs = qs.filter(
        Q(start_date__gte=start_date,
          end_date__lte=end_date)
        | Q(start_date__lte=start_date,
            end_date__gte=end_date)
    )
    # qs = qs1|qs2

    if qs.count() >= room_count:
        return False
    return True


def index(request):
    amenities = Amenity.objects.all()
    hotels = Hotel.objects.all()
    total_hotels = len(hotels)  
    selected_amenities = request.GET.getlist('selectAmenity')
    sort_by = request.GET.get('sortSelect')
    search = request.GET.get('searchInput')
    startdate = request.GET.get('startDate')
    enddate = request.GET.get('endDate')
    price = request.GET.get('price')

    if selected_amenities != []:
        hotels = hotels.filter(
            amenities__amenity_name__in=selected_amenities).distinct()
    if search:

        hotels = hotels.filter(Q(hotel_name__icontains=search)
                               | Q(description__icontains=search) | Q(amenities__amenity_name__contains=search))
        

    if sort_by:

        if sort_by == 'low_to_high':
            hotels = hotels.order_by('hotel_price')

        elif sort_by == 'high_to_low':
            hotels = hotels.order_by('-hotel_price')
    if price:

        hotels = hotels.filter(hotel_price__lte=int(price))

    if startdate and enddate:

        unbooked_hotels = []
        for i in hotels:
            valid = check_booking(i.id, i.room_count, startdate, enddate)
            if valid:
                unbooked_hotels.append(i)
        hotels = unbooked_hotels
    hotels = hotels.distinct ()
    p = Paginator(hotels, 2)
    page_no = request.GET.get('page')

    hotels = p.get_page(1)

    if page_no:
        hotels = p.get_page(page_no)
    no_of_pages = list(range(1, p.num_pages+1))

    date = datetime.today().strftime('%Y-%m-%d')

    context = {'amenities': amenities, 'hotels': hotels, 'sort_by': sort_by,
               'search': search, 'selected_amenities': selected_amenities, 'no_of_pages': no_of_pages, 'max_price': price, 'startdate': startdate, "enddate": enddate, "date": date,'total_hotels':total_hotels}
    return render(request, 'home/index.html', context)



def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = authenticate(request, username=username, password=password)

        if user_obj:
            if user_obj.is_active:
                login(request, user_obj)
                messages.success(request, 'Sign-in Successful')
                return redirect('/')
            else:
                messages.error(request, 'This account is inactive.')
                return redirect('signin')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('signin')

    return render(request, 'home/signin.html')



def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Check if the username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose a different username.')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return redirect('signup')

        # Create a new user and hash the password
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        customer = Customer.objects.create(
            user=user,
            phone=phone,
            address=address
        )
        customer.save()

        messages.success(request, 'Welcome! Signup Successful.')
        return redirect('signin')

    return render(request, 'home/signup.html')

def signout(request):
    logout(request)
    return redirect('/')


def get_hotel(request, id):
    hotel = get_object_or_404(Hotel, id=id)
    context = {'hotel': hotel}
    context['date'] = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        checkin = request.POST.get('startDate')
        checkout = request.POST.get('endDate')
        context['startdate'] = checkin
        context['enddate'] = checkout

        # Validate dates
        try:
            valid = check_booking(
                hotel.id, hotel.room_count, checkin, checkout)
            if not valid:
                messages.error(request, 'Booking for these days are full')
                return render(request, 'home/hotel.html', context)
        except:
            messages.error(request, 'Please Enter Valid Date Data')
            return render(request, 'home/hotel.html', context)

        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return render(request, 'home/hotel.html', context)


        # Check room availability
        available_rooms = hotel.rooms.filter(is_Booked=False)

        if not available_rooms.exists():
            messages.error(request, 'No rooms available for the selected dates.')
            return render(request, 'home/hotel.html', context)

        # Get the first available room
        room_to_book = available_rooms.first()

        try:
            customer = request.user.customer_profile
        except Customer.DoesNotExist:
            messages.error(request, "Please complete your profile before booking a hotel.")
            return redirect('profile_update')

        tax = Taxes.objects.first()  # Example: gets the first available tax


        # Create booking and booking room
        customer = get_object_or_404(Customer, user=request.user)
        booking = Booking.objects.create(
            customer=customer,
            hotel=hotel,
            room=room_to_book,
            tax=tax,  # Add appropriate tax handling
            status=Booking.StatusChoices.PENDING,
            start_date=checkin_date,
            end_date=checkout_date
        )
        
        BookingRoom.objects.create(booking=booking, room=room_to_book)
        room_to_book.is_Booked = True
        room_to_book.save()

        messages.success(request, f'{hotel.name} booked successfully. Your booking ID is {booking.id}.')
        return render(request, 'home/hotel.html', context)

    return render(request, 'home/hotel.html', context)

def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user.customer_profile)
    return render(request, 'home/my_bookings.html', {'bookings': bookings})

def cancel_booking(request, booking_id):
    # Get the booking, ensure it belongs to the current logged-in customer
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user.customer_profile)

    # Check if the booking is already canceled
    if booking.status != Booking.StatusChoices.CANCELED:
        booking.status = Booking.StatusChoices.CANCELED
        booking.save()

        booking.room.is_Booked = False
        booking.room.save()

        #deleting the associated booking room entry
        booking_room = get_object_or_404(BookingRoom, booking=booking, room=booking.room)
        booking_room.delete()

        messages.success(request, f'Your booking with ID {booking.id} has been successfully cancelled.')
    else:
        messages.error(request, 'This booking has already been cancelled.')

    # Redirect back to the user's bookings page
    return redirect('my_bookings')

def pay_booking(request, booking_id):
    # Fetch the booking to be paid
    booking = get_object_or_404(Booking, id=booking_id)

    # Handle payment logic here
    # For now, we will just render a simple payment confirmation page
    if request.method == 'POST':
        # Update the booking status to "Completed" once payment is made
        booking.status = Booking.StatusChoices.CONFIRMED
        booking.save()

        booking.room.is_Booked = True
        booking.room.save()

        messages.success(request, f'Your booking with ID {booking.id} has been successfully Confirmed.')

        # Redirect to a success page
        return redirect('my_bookings')

    # Render the payment page
    return render(request, 'home/pay_booking.html', {'booking': booking})


def hotel_list(request):
    hotels = Hotel.objects.prefetch_related('rooms').all()
    return render(request, 'your_template.html', {'hotels': hotels})

def profile_update(request):
    # Your logic for updating the profile
    return render(request, 'profile_update.html')