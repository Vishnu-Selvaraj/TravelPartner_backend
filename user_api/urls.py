from django.urls import path
from . import views


urlpatterns = [

    path('signup',views.user_signup,name='signup'),
    path('login',views.user_login,name='login'),
    path('change-password',views.user_change_password,name='user_change_password'),
    path('logout',views.user_logout,name='logout'),



    path('get-user-data',views.get_user_data,name='get_user_details'),
    path('edit-user-data',views.update_user_data,name='edit_user_details'),


    path('get-homepage-tour-data',views.get_data_for_home_page,name='get_data_for_home_page'),
    path('get-all-tour-list',views.get_all_tour_data,name='get_tour_data'),
    path('get-view-tour-details/<int:tour_id>/',views.get_view_tour_data,name='get_view_tour_data'),

    path('add-user-booking/<int:tour_id>/',views.add_user_bookings,name='add_user_booking'),
    path('get-all-user-booking/<str:user_select_option>/',views.get_all_user_bookings,name='get_all_user_bookings'),
    path('cancel-user-booking/',views.cancel_user_booking,name='cancel_user_booking'),


    path('get-confirmation-details/<int:tour_id>/',views.get_booking_confirmation_details,name='get_confirmation_details'),
    path('get-user-booking-pdf/<str:booking_id>/',views.download_user_booking_pdf,name='download_user_booking_pdf')



]