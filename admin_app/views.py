from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from user_api.models import User,UserBookings
from .models import TourList,Itinerary
# from .forms import itineraryFormset
from django.contrib import messages # using django inbuild message system to show success and errors
import re
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.

#check whether the user is superuser or not.
def check_is_superuser(user):
    return user.is_superuser

#LOGIN
def admin_login(request):

    email = request.POST.get('email')
    password = request.POST.get('password')

    if request.method == 'POST':
        if not email or not password:
            messages.error(request,'Please fill both the fields.')
            return redirect('/')
        else:
            user = authenticate(username = email , password = password)
            if user:
                if check_is_superuser(user):
                    login(request,user)
                    messages.success(request,"logined successfully.")
                    return redirect('/get-tour-plans')
                else:
                    messages.error(request,"Sorry, you don't have permission to access this page")
                    return redirect('/')
            else:
                messages.error(request,'Invalid Credentials.')
                return redirect('/')
    return render(request,'auth/admin_login_page.html')

def is_password_strong(password):
    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d#@$!%*?&]{8,}$'
    if password is None:
        return False
    return bool(re.match(pattern,password)) # return True or False

#CHANGE_PASSWORD
@login_required(login_url='/')
def admin_change_password(request):

    user = request.user
    current_password = request.POST.get('currentPassword')
    new_password = request.POST.get('newPassword')
    password_confirm = request.POST.get('passwordConf')

    if not check_is_superuser(user):
        messages.error(request,"Sorry, you don't have permission to access this page")
        return redirect('/')


    if request.method == 'POST':
        if not current_password or not new_password or not password_confirm:
            messages.error(request,'All fields required')
            return redirect('/admin-change-password')
        elif new_password != password_confirm:
            messages.error(request,'Passwords does not match')
            return redirect('/admin-change-password')
        elif not is_password_strong(new_password):
            messages.error(request,'Password is too weak.Password must be at least 8 characters long with at least one capital letter and symbol.')
            return redirect('/admin-change-password')
        elif not user.check_password(current_password):
            messages.error(request,'Incorrect current password.')
            return redirect('/admin-change-password')
        else:
            user.set_password(new_password)
            user.save()
            return redirect('/')     
    return render(request,'auth/admin_change_password_page.html')

@login_required(login_url='/')
        
def admin_logout(request):
    if request.method == 'GET':
        logout(request)
        print('loggned out')
        return redirect('/')
    return render(request,'auth/admin_login_page.html')

#Check image the file type is valid

def check_image_file_type(image):
    IMAGE_FILE_TYPES = ['jpg', 'jpeg','png']
    tour_instance = TourList()
    tour_instance.image = image
    image_file_type = tour_instance.image.url.split('.')[-1]
    if image_file_type.lower() in IMAGE_FILE_TYPES:
        return True
    else:
        return False    


# def create_tour_plans(request):

#     new_place_name = request.POST.get('placeName')
#     new_description = request.POST.get('description')
#     new_price = request.POST.get('price')
#     new_image = request.FILES.get('image')
#     new_total_trip_days = request.POST.get('tripDays')

#     itinerary_Form = itineraryFormset(request.POST)
#     print(request.POST , request.FILES)
#     # form = TourForm()

#     if request.method == 'POST':
#         if not new_place_name or not new_description or not new_price or not new_image or not new_total_trip_days:
#             messages.error( request,'Please fill all fields')
#             return redirect('/add-tour-plans')
#         if not check_image_file_type(new_image):
#             messages.error( request,'Invalid thumbanil file type. Please upload an image in JPG, JPEG, or PNG format.')
#             return redirect('/add-tour-plans')
#         else:
#             if itinerary_Form.is_valid():
#                 new_tour_instance = TourList(place_name = new_place_name,description = new_description,
#                                         price = new_price,image = new_image,total_trip_days=new_total_trip_days)
                

#     return render(request,'tour_pages/admin_tour_create_page.html',{'itinerary_Form':itinerary_Form})

#Add new tour details
@login_required(login_url='/')

def create_tour_plans(request):

    new_place_name = request.POST.get('placeName')
    new_description = request.POST.get('description')
    new_price = request.POST.get('price')
    new_image = request.FILES.get('image')
    new_total_trip_days = request.POST.get('tripDays')
    if request.method == 'POST':
        print(request.POST , request.FILES)
        if not new_place_name or not new_description or not new_price or not new_image or not new_total_trip_days:
            messages.error( request,'Please fill all fields')
            return redirect('/add-tour-plans')
        if not check_image_file_type(new_image):
            messages.error( request,'Invalid thumbanil file type. Please upload an image in JPG, JPEG, or PNG format.')
            return redirect('/add-tour-plans')
        else: 
            new_tour_instance = TourList(place_name = new_place_name,description = new_description,
                                         price = new_price,image = new_image,total_trip_days= new_total_trip_days)
            new_tour_instance.save()
            return redirect('/get-tour-plans')
    return render(request,'tour_pages/admin_tour_create_page.html')

# Get tour details   
@login_required(login_url='/')

def get_tour_list(request):
    if request.method == 'GET':
        search_term = request.GET.get('term')
        is_clicked_search_btn = False
        if search_term:
            instance = TourList.objects.filter(place_name__icontains = search_term)
            is_clicked_search_btn = True
            if not instance.exists():
                messages.error(request,'No tour data Found')           
        else:
            instance = TourList.objects.all()
        paginator = Paginator(instance,2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,'tour_pages/admin_tour_list_page.html',{'tour_data':page_obj,'is_clicked_search_btn':is_clicked_search_btn})


# Get individual tour details   
@login_required(login_url='/')

def get_tour_view_data(request,tour_id):

    if request.method == 'GET':
        try:
            tour_itinerary_instance = Itinerary.objects.filter(tour = tour_id).order_by('day')
            tour_instance = TourList.objects.get(pk = tour_id)
            print([data.tour.place_name  for data in tour_itinerary_instance ])
        except Itinerary.DoesNotExist:
            messages.error(request,'Invalid tour place id')
            return redirect('/get-tour-plans')
        return render(request,'tour_pages/admin_tour_view_page.html',{'tour_instance':tour_instance,'tour_itinerary_instance':tour_itinerary_instance})
    return render(request,'tour_pages/admin_tour_list_page.html')

# Edit tour details  
@login_required(login_url='/')
 
def edit_tour_details(request,tour_id):
    try:
        edit_tour_instance = TourList.objects.get(pk = tour_id)
    except TourList.DoesNotExist:
        messages.error(request,'Invalid tour place id')
        return redirect(f'/edit-tour-detail/{tour_id}')
    
    if request.method == 'POST':
        edited_place_name = request.POST.get('placeName')
        edited_description = request.POST.get('description')
        edited_price = request.POST.get('price')
        edited_image = request.FILES.get('image')
        edited_total_trip_days = request.POST.get('tripDays')
        if not edited_place_name or not edited_description or not edited_price or not edited_total_trip_days:
            messages.error( request,'Please fill all fields')
            return redirect(f'/edit-tour-detail/{tour_id}')
        if edited_image and not check_image_file_type(edited_image):
            messages.error( request,'Invalid thumbanil file type. Please upload an image in JPG, JPEG, or PNG format.')
            return redirect(f'/edit-tour-detail/{tour_id}')
        else: 
            if edited_image:
                edit_tour_instance.image = edited_image
            edit_tour_instance.place_name = edited_place_name
            edit_tour_instance.description = edited_description
            edit_tour_instance.price = edited_price
            edit_tour_instance.total_trip_days = edited_total_trip_days
            edit_tour_instance.save()
            messages.success( request,'Tour details updated succesfully.')
            return redirect(f'/edit-tour-detail/{tour_id}')
    return render(request,'tour_pages/admin_tour_edit_page.html',{'edit_tour_instance':edit_tour_instance})

#Delete tour details
@login_required(login_url='/')

def delete_tour_details(request,tour_id):
    if request.method == 'GET':
        try:
            delete_instance = TourList.objects.get(pk = tour_id)
        except TourList.DoesNotExist:
            messages.error(request,'Tour details could not be found.')
            return redirect('/get-tour-plans')
        else:
            delete_instance.delete()
            messages.success(request,'Tour details deleted successfully.')
            return redirect('/get-tour-plans')
            

# ADD itinerary details
@login_required(login_url='/')

def add_itinerary(request,tour_id):

    day = request.POST.get('day')
    activity = request.POST.get('activity')
    print(request.POST)
    if request.method == 'POST':
        try:
            instance = TourList.objects.get(pk = tour_id)
        except TourList.DoesNotExist:
            messages.error(request,'Invalid tour place id')
            return redirect(f'/add-tour-plans-itinerary/{tour_id}')

        if not day or not activity:
            messages.error(request,'please fill both fields')
            return redirect(f'/add-tour-plans-itinerary/{tour_id}')

        no_of_itineraries_added = Itinerary.objects.filter(tour = tour_id).aggregate(count = Count(id)).get('count')   
        
        #This condition to check whether the number of total trip days is equal to the no_of_itineraries_added in Itinerary table
        if no_of_itineraries_added >= instance.total_trip_days:
            messages.error(request,f'You have already added details for all {instance.total_trip_days} itinerary days.')
            return redirect(f'/add-tour-plans-itinerary/{tour_id}')

        else:
            new_itinerary = Itinerary(tour = instance,day = day ,activities = activity)
            new_itinerary.save()
            print(tour_id)
            messages.success(request,'Itinerary successfully added.')
            return render(request,'tour_pages/admin_add_itinerary.html')

    return render(request,'tour_pages/admin_add_itinerary.html')

# Edit itinerary details
@login_required(login_url='/')

def edit_itinerary(requset,tour_id):
    try:
        itinerary_instance = Itinerary.objects.filter(tour = tour_id)
    except Itinerary.DoesNotExist:
        messages.error(requset,'No data Found')
        return redirect(f'/edit-tour-itinerary-detail/{tour_id}')
    
    if requset.method == 'POST':
        day = requset.POST.get('day')
        activity = requset.POST.get('activity')
        update_itinerary = Itinerary.objects.filter(day = day,tour = tour_id).first()
        update_itinerary.day = day
        update_itinerary.activities = activity
        update_itinerary.save()
        print(update_itinerary)
        messages.success(requset,f'The day {day} itinerary details updated successfully')
        return redirect(f'/edit-tour-itinerary-detail/{tour_id}')

    return render(requset,'tour_pages/admin_edit_itinerary.html',{'itinerary_instance':itinerary_instance})

# Delete itinerary details
@login_required(login_url='/')
def delete_itinerary(request,tour_id):
    if request.method == 'POST':
        print(request.POST)
        day = request.POST.get('day')
        try:
            del_instance = Itinerary.objects.filter(day = day,tour = tour_id).first()
        except Itinerary.DoesNotExist:
            messages.error(request,'Invalid day number. Please enter a valid day.')
            return redirect('/get-tour-plans')
        else:
            if del_instance == None:
                messages.error(request,'Invalid day number. Please enter a valid day.')
                return redirect('/get-tour-plans')
            else:
                del_instance.delete()
                messages.success(request,'The entered itinerary day was deleted successfully.')
                return redirect('/get-tour-plans')
            
# GET USER DETAILS

@login_required(login_url='/')
def get_all_user_details(request):

    if request.method == 'GET':
        search_term = request.GET.get('search_name')
        is_clicked_search_btn = False
        if search_term:
            instance = User.objects.filter(Q(name__icontains = search_term) | Q(email__icontains = search_term))
            is_clicked_search_btn = True
            if not instance.exists():
                messages.error(request,'No tour data Found')           
        else:
            instance = User.objects.filter(is_superuser__exact = False)
        paginator = Paginator(instance,2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    return render(request,'tour_pages/user_page/admin_user_list_page.html',{'users_data':page_obj,'is_clicked_search_btn':is_clicked_search_btn})


#CHECK USER BLOCKED OR UNBLOCKED

def user_block_or_unblock(request,user_id):
    try:
        user_data = User.objects.filter(pk = user_id).first()
    except User.DoesNotExist:
        messages.error(request,'User not Found')
        return redirect('/get-all-user-details')
    else:
        if user_data.is_blocked == True:
            user_data.is_blocked = False
            user_data.save()
            messages.success(request,'User Unblocked Successfully.')
            return redirect('/get-all-user-details')
        else:
            user_data.is_blocked = True
            user_data.save()
            messages.error(request,'User Blocked Successfully.')
            return redirect('/get-all-user-details')

# GET USER DETAILED VIEW

def admin_view_get_all_user_bookings(request,user_id):
    try:
        user_bookings = UserBookings.objects.filter(user = user_id).order_by('-created_at')
    except UserBookings.DoesNotExist:
        return render(request,'tour_pages/user_page/admin_user_bookings.html')
    else:
        paginator = Paginator(user_bookings,2)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'tour_pages/user_page/admin_user_bookings.html',{'user_bookings':page_obj})
