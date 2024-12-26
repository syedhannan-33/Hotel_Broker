
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from home.models import *
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Min, Max
from decimal import Decimal



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
    hotels = Hotel.objects.all().order_by('name')
    total_hotels = len(hotels)
    sort_by = request.GET.get('sortSelect')
    search = request.GET.get('searchInput')
    price = request.GET.get('price')

   

    if search:
        hotels = hotels.filter(
            Q(name__icontains=search) |  # Search in hotel name
            Q(location__city__icontains=search) |  # Search in city
            Q(location__state__icontains=search) |  # Search in state
            Q(location__country__icontains=search)  # Search in country
        ).distinct()

    if sort_by:
        if sort_by == 'low_to_high':
            # Get the minimum price for each hotel based on room prices
            hotels = hotels.annotate(min_price=Min('rooms__price_per_night')).order_by('min_price')
        elif sort_by == 'high_to_low':
            # Get the maximum price for each hotel based on room prices
            hotels = hotels.annotate(max_price=Max('rooms__price_per_night')).order_by('-max_price')


    hotels = hotels.distinct()
    p = Paginator(hotels, 5)
    page_no = request.GET.get('page')

    hotels = p.get_page(1)
    if page_no:
        hotels = p.get_page(page_no)

    no_of_pages = list(range(1, p.num_pages + 1))
    date = datetime.today().strftime('%Y-%m-%d')

    context = {
        'hotels': hotels,
        'sort_by': sort_by,
        'search': search,
        'no_of_pages': no_of_pages,
        'max_price': price,
        'date': date,
        'total_hotels': total_hotels
    }
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
        broom_type = request.POST.get('roomType')  # Capture selected room type

        context['startdate'] = checkin
        context['enddate'] = checkout
        context['roomType'] = broom_type  # Add selected room type to context for the template
        print(f"Selected room type: {broom_type}")
        broom_type = broom_type.capitalize()

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

        if(checkin_date > checkout_date):
            messages.error(request, 'Invalid Date Selection')
            return render(request, 'home/hotel.html', context)

        # Filter available rooms based on the selected room type
        # Filter available rooms based on the selected room type (using 'type' instead of 'room_type')
        available_rooms = hotel.rooms.filter(is_Booked=False, room_type=broom_type)
        print(f"Selected room type: {available_rooms}")


        if not available_rooms.exists():
            messages.error(request, 'No rooms available for the selected dates and room type.')
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

    # Calculate the number of nights and the total cost
    start_date = booking.start_date
    end_date = booking.end_date
    num_nights = (end_date - start_date).days

    # Get the tax rate from the hotel's tax class
    tax_rate = booking.tax.percentage if booking.tax else 0

    # Calculate the total amount
    price_per_night = booking.room.price_per_night
    sub_total = num_nights * price_per_night
    tax = sub_total * (tax_rate/Decimal(100))
    total = sub_total + tax

    if request.method == 'POST':
        # Update the booking status to "Confirmed" once payment is made
        booking.status = Booking.StatusChoices.CONFIRMED
        booking.save()

        booking.room.is_Booked = True
        booking.room.save()

        Payments.objects.create(
            booking=booking,
            date=datetime.now(),
            Amount=total,
            method=Payments.MethodChoice.Online,  # Assuming payment is online; modify as needed
            Status=Payments.StatusChoice.Paid
        )

        messages.success(request, f'Your booking with ID {booking.id} has been successfully confirmed.')

        # Redirect to a success page
        return redirect('my_bookings')

    # Render the payment page with calculated values
    return render(request, 'home/pay_booking.html', {
        'booking': booking,
        'num_nights': num_nights,
        'price_per_night': price_per_night,
        'sub_total': sub_total,
        'tax': tax,
        'total': total,
    })



def hotel_list(request):
    hotels = Hotel.objects.prefetch_related('rooms').all()
    return render(request, 'your_template.html', {'hotels': hotels})

def profile_update(request):
    # Your logic for updating the profile
    return render(request, 'profile_update.html')