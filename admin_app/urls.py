from django.urls import path
from . import views


urlpatterns = [
    path('',views.admin_login,name='login'),
    path('admin-change-password/',views.admin_change_password,name='change_password'),
    path('add-tour-plans/',views.create_tour_plans,name='create'),
    path('logout',views.logout,name='admin_logout'),

    path('get-tour-plans/',views.get_tour_list,name='get_tour_list'),
    path('get-tour-detail-view/<int:tour_id>/',views.get_tour_view_data,name='get_tour_detail_view'),
    path('edit-tour-detail/<int:tour_id>/',views.edit_tour_details,name='edit_tour_details'),
    path('delete-tour-detail/<int:tour_id>/',views.delete_tour_details,name='delete_tour_details'),

    path('add-tour-plans-itinerary/<int:tour_id>/',views.add_itinerary,name='add_itinerary'),
    path('edit-tour-itinerary-detail/<int:tour_id>/',views.edit_itinerary,name='edit_itinerary'),
    path('delete-tour-itinerary-detail/<int:tour_id>/',views.delete_itinerary,name='delete_itinerary'),

    path('get-all-user-details/',views.get_all_user_details,name='get_all_user_details'),
    path('get-user-all-bookings/<int:user_id>/',views.admin_view_get_all_user_bookings,name='admin_view_get_all_user_bookings'),
    path('block-unblock-user/<int:user_id>/',views.user_block_or_unblock,name='user_block_or_unblock'),


    # path('admin-signup/',views.admin_signup,name='signup'),

]
