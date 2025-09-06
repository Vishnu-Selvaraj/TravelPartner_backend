from rest_framework import serializers
from admin_app.models import TourList,Itinerary
from .models import User,UserBookings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','email','phone_number']
    

class TourListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourList
        fields = '__all__'

class TourItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = '__all__'

class CreateUserbookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookings
        fields = ['number_of_persons','total_price','trip_start_date']
        

class GetAllUserbookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookings
        fields = '__all__'
        