# from .models import TourList,Itinerary
# from django import forms
# from django.forms import inlineformset_factory


# class TourForm(forms.ModelForm):
#     class Meta:
#         model = TourList
#         fields = ['place_name','description','price','image','total_trip_days']

# class ItineraryForm(forms.ModelForm):
#     class Meta:
#         model = Itinerary
#         fields = ['day','activities']


# itineraryFormset = inlineformset_factory(
#                 TourList,
#                 Itinerary,
#                 form= ItineraryForm, 
#                 fields=['day','activities'] ,
#                 extra = 1 ,
#                 can_delete=True)
