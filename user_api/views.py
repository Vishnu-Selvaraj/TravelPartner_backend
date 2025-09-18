from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate,login,logout

from django.template.loader import render_to_string,get_template
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse

from xhtml2pdf import pisa
from io import BytesIO

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import User,UserBookings
from admin_app.models import TourList,Itinerary
from .serializers import TourListSerializer,TourItinerarySerializer,UserSerializer,CreateUserbookingsSerializer,GetAllUserbookingsSerializer

import string
import random
from django.utils import timezone


# Create your views here.

#Normalize email

def normalize_email(email):
    if email:
        email.strip().lower()
        return email

# USER SIGNUP
@api_view(['POST'])
@permission_classes((AllowAny,))
def user_signup(request):
    name = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')

    validate_email = EmailValidator()

    if not name:
        return Response({'error':'Name field is required'},status=status.HTTP_400_BAD_REQUEST)
    elif not email:
        return Response({'error':'Please provide an email address in the proper format.'},status=status.HTTP_400_BAD_REQUEST)
    elif not password:
        return Response({'error':'password field is required'},status=status.HTTP_400_BAD_REQUEST)
    
    #Email format validation

    try:
        validate_email(email)
    except ValidationError as error:
        return Response({'error':error},status=status.HTTP_400_BAD_REQUEST)
    
    #Check whether email exists or not

    if User.objects.filter(email__exact = email).exists():
        return Response({'error':'Email already exists'},status = status.HTTP_400_BAD_REQUEST )
    else:
        email = normalize_email(email)
        newUser = User(name = name,email = email,username = email)
        newUser.set_password(password)
        newUser.save()
        return Response({'message':'Account created successfully'},status = status.HTTP_201_CREATED )

#CHECK USER BLOCKED OR NOT

def check_user_blocked_or_not(request_user):
    if request_user.is_blocked:
        return True
    else:
        return False


#USER LOGIN 

@api_view(['POST'])
@permission_classes((AllowAny,))
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email:
        return Response({'error':'Email field is required.'},status=status.HTTP_400_BAD_REQUEST)
    elif not password:
        return Response({'error':'Password field is required.'},status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username = email,password = password)

    if not user:
        return Response({'error':'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED) 
    if check_user_blocked_or_not(user):
        return Response({'error':'Your account has been blocked. Please contact support for assistance.'},status=status.HTTP_401_UNAUTHORIZED) 
    else:
        login(request,user)
        token,_ = Token.objects.get_or_create(user = user)
        return Response({'message':'Logged in successfully.','token':token.key},status=status.HTTP_200_OK)
       

#USER LOGOUT  

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def user_logout(request):
    user = request.user
    if user:
        logout(request)
        return Response({'message':'Logged out successfully'},status=status.HTTP_200_OK)
    return Response({'error':'You are not logged in yet!'},status=status.HTTP_401_UNAUTHORIZED)

#USER CHANGE PASSWORD

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_change_password(request):
    user = request.user
    current_password = request.data.get('currentPassword')
    new_password = request.data.get('newPassword')

    if user.check_password(current_password):
        user.set_password(new_password)
        user.save()
        return Response({'message':'Password updated successfully.'},status=status.HTTP_200_OK)
    return Response({'error':'The current password is incorrect.'},status=status.HTTP_400_BAD_REQUEST)


#GET USER PROFILE DATA

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_user_data(request):
    user = request.user
    
    try:
        user_data = User.objects.get(pk = user.id)
    except User.DoesNotExist:
        return Response({'error':'No user data found'},status=status.HTTP_400_BAD_REQUEST)
    else:
        user_serializer = UserSerializer(user_data)
        return Response({'data':user_serializer.data},status= status.HTTP_200_OK)
    

#UPDATE USER PROFILE DATA

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def update_user_data(request):
    user = request.user

    name = request.data.get('name')
    email = request.data.get('email')
    phoneNo = request.data.get('phoneNumber')

    if not name and not email and not phoneNo:
        return Response({'error':'Please fill all the fields.'},status= status.HTTP_400_BAD_REQUEST)
    elif not name:
        return Response({'error':'Name field required.'},status= status.HTTP_400_BAD_REQUEST)
    elif not email:
        return Response({'error':'Email field required.'},status= status.HTTP_400_BAD_REQUEST)
    elif not phoneNo:
        return Response({'error':'Phone Number field required.'},status= status.HTTP_400_BAD_REQUEST)
    # int has no len function so converting it into str
    elif len(str(phoneNo)) != 10:
        return Response({'error':'Invalid phone number.'},status= status.HTTP_400_BAD_REQUEST)
    #Check whether phone already exists or not
    elif User.objects.filter(phone_number = phoneNo).exclude(id = user.id).exists():
        return Response({'error':'Phone number already in use.'},status= status.HTTP_400_BAD_REQUEST)

    #If user email changed or not
    if email != user.email:
        print(request.data)
        user_serializer = UserSerializer(user,data = request.data,partial = True) # here user that mention the particular user instance and partial used for partial update
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'message':'Profile updated successfully'},status= status.HTTP_200_OK)
    else:
        user.name = name
        user.phone_number = phoneNo
        user.save()
        return Response({'message':'Profile updated successfully'},status= status.HTTP_200_OK)
        
    return Response({'error':user_serializer.errors},status= status.HTTP_400_BAD_REQUEST)

# GET DATA FOR HOME PAGE
@api_view(['GET'])
@permission_classes((AllowAny,))

def get_data_for_home_page(request):

    try:
        tour_data = TourList.objects.all().order_by('-created_at')[:5] # ADDED LIMIT ON GETTING DATA
    except TourList.DoesNotExist:
        return Response({'error':'No data found'},status=status.HTTP_400_BAD_REQUEST)
    else:
        serialized_data = TourListSerializer(tour_data,many = True)
        return Response({'data':serialized_data.data},status=status.HTTP_200_OK)


#GET ALL TOUR DETAILS

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_all_tour_data(request):

    if not check_user_blocked_or_not(request.user):
        try:
            tour_data = TourList.objects.all().order_by('-created_at') 
        except TourList.DoesNotExist:
            return Response({'error':'No data found'},status=status.HTTP_400_BAD_REQUEST)
        else:
            serialized_data = TourListSerializer(tour_data,many = True)
            return Response({'data':serialized_data.data},status=status.HTTP_200_OK)
    else:
        return Response({'blocked_error':'Your account has been blocked. Please contact support for assistance.'},status=status.HTTP_401_UNAUTHORIZED) 

#GET INDIVIDUAL TOUR AND ITINERARY DATA

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_view_tour_data(request,tour_id):

    try:
        view_itinerary_instance = Itinerary.objects.filter(tour = tour_id).order_by('day')
    except Itinerary.DoesNotExist:
        return Response({'error':'Unfortunately, we are unable to find the tour details.'},status=status.HTTP_400_BAD_REQUEST)
    else:
        #By using foreign key accessing the tour details. 
        #Using first() getting the single object from the Queryset of itineraries 
        view_tour_instance = view_itinerary_instance.first()
        if not view_tour_instance:
            return Response({'error':'Unfortunately, we are unable to find the tour details.'},status=status.HTTP_400_BAD_REQUEST)
        tour_serializer_instance = TourListSerializer(view_tour_instance.tour) # tour(foreign key) which refers the tourList table
        itinerary_serializer = TourItinerarySerializer(view_itinerary_instance,many = True)
        return Response({'data': {'tour_data':tour_serializer_instance.data,'itinerary':itinerary_serializer.data}},status=status.HTTP_200_OK)


#BOOKING CONFIRMATION MAIL

def send_confirmation_mail(user ,tour_id):

    user_booking_data = UserBookings.objects.filter(user = user , tour = tour_id).first()
    subject = f"Booking Details: {'TRAVELPATNER'}"
    from_email = "user123@gmail.com"
    recipient_list = ["your_mailtrap_inbox@mailtrap.io"]
    html_message = render_to_string('booking_email.html', {'bookingData': user_booking_data})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


#ADD USER BOOKINGS

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user_bookings(request,tour_id):
    user = request.user

    try:
        tour_instance = TourList.objects.get(pk = tour_id)
    except TourList.DoesNotExist:
        return Response({'error':'Tour not found.'},status=status.HTTP_400_BAD_REQUEST)


    booking_instance_serializer = CreateUserbookingsSerializer(data = request.data)
    if booking_instance_serializer.is_valid():
        bookingId = ''.join(random.choices(string.ascii_uppercase + string.digits,k=8))

        #Check whether the booking id already exists or not
        if UserBookings.objects.filter(booking_id__exact = bookingId).exists():
            bookingId = ''.join(random.choices(string.ascii_uppercase + string.digits,k=8))
        #Check whether user provided phone number or not
        if not user.phone_number:
            return Response({'error':'Phone number not provided.'},status= status.HTTP_400_BAD_REQUEST)
        else:
            print('Called')
            booking_instance_serializer.save(tour = tour_instance,user = user,booking_id = bookingId)
            send_confirmation_mail(user,tour_id)

            return Response({'message':'Booking added successfully.'},status=status.HTTP_201_CREATED)
    else:
        return Response({'error':booking_instance_serializer.errors},status=status.HTTP_400_BAD_REQUEST)

#CANCEL USER BOOKING

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_user_booking(request):
    request_user = request.user
    user_booking_id = request.data.get('user_booking_id')
    print(user_booking_id)
    try:
        booking_instance = UserBookings.objects.filter(user = request_user,booking_id__exact = user_booking_id ).first()
    except UserBookings.DoesNotExist:
        return Response({'error':'Booking not found.'},status=status.HTTP_400_BAD_REQUEST)
    else:
        today_date = timezone.now().date()
        trip_start_date = booking_instance.trip_start_date.date()
        if(today_date < trip_start_date):
            booking_instance.delete()
            return Response({'message':'Booking Successfully cancelled.'},status=status.HTTP_200_OK)
        
        return Response({'error':"This booking cannot be canceled. Please contact us if you have any queries."}, status=status.HTTP_406_NOT_ACCEPTABLE)
        


#BOOKING CONFIRMATION REQUEST

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def get_booking_confirmation_details(request,tour_id):
    user = request.user
    try:
        user_booking_instance = UserBookings.objects.filter(user = user, tour=tour_id).order_by('-created_at').first()
    except UserBookings.DoesNotExist:
        return Response({'error':'Invalid Booking ID.'},status= status.HTTP_400_BAD_REQUEST)

    user_booking_confirm_serializer = GetAllUserbookingsSerializer(user_booking_instance)
    return Response({'data':user_booking_confirm_serializer.data,'place_name':user_booking_instance.tour.place_name},status=status.HTTP_200_OK)


#Check whether user have any bookings and return that data
def check_user_booking_upcoming_or_not(user,user_select_option):
    try:
        all_user_bookings = UserBookings.objects.filter(user = user).order_by('-trip_start_date')
    except UserBookings.DoesNotExist:
        return False
    
    upcoming_trips = []
    previous_trips = []
    
    if len(all_user_bookings) == 0:
        return []
    else:
        for data in all_user_bookings:
            today_date = timezone.now()
            total_trip_days = data.tour.total_trip_days
            date_of_trip_start = data.trip_start_date
            difference_in_dates = (today_date - date_of_trip_start).days # calculating the difference in days
            total_days_left = total_trip_days - difference_in_dates 
            print(total_days_left)

            if total_days_left < 0:
                previous_trips.append(data)
            if total_days_left >= 0 and date_of_trip_start >= today_date:
                upcoming_trips.append(data)

    print(user_select_option)
    if user_select_option == 'Upcoming':
        return upcoming_trips
    if user_select_option == 'Previous':
        return previous_trips


#GET USER BOOKINGS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_user_bookings(requset,user_select_option):
    user = requset.user
    trip_data = check_user_booking_upcoming_or_not(user,user_select_option)
    user_booking_tour_data = [data.tour for data in trip_data]
    if not trip_data:
        return Response({'error':'No bookings found'},status= status.HTTP_400_BAD_REQUEST)
    else:
        user_bookings_serializer = GetAllUserbookingsSerializer(trip_data,many = True)
        user_booking_tour_serializer = TourListSerializer(user_booking_tour_data, many = True)
        print(user_booking_tour_serializer.data)

        ## ** means unpacking of two dicts and zip function that retuen an object of joined data of tuple
        combined_data = [{**item1,**item2} for item1,item2 in zip(user_bookings_serializer.data,user_booking_tour_serializer.data)]
        merged_data = [combinedItem for combinedItem in combined_data]

        print(merged_data)
        

    return Response({'user_booking_data':merged_data},status= status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_user_booking_pdf(request,booking_id):

    user = request.user
    try:
        user_booking = UserBookings.objects.filter(booking_id = booking_id).order_by('-created_at').first()
    except UserBookings.DoesNotExist:
        return Response('Unable to get booking Details')
    
    else:
        print(user_booking.tour.place_name)
        template = get_template('booking_pdf.html')
        html_template = template.render({'Booking_details':user_booking})

        buffer = BytesIO()
        html_template = html_template.encode('utf-8')
        pisa_status = pisa.CreatePDF(html_template,dest=buffer)

        if pisa_status.err:
            return HttpResponse('PDF creation error!')
        else:
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(user_booking.tour.place_name)
            return response
        


        