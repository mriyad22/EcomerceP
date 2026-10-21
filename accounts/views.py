from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import *
from .models import *

from django.views.decorators.http import require_POST   # To use a function as a POST method

from orders.models import AddressModel


#------>User Registation here
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form_data = UserRegistationForm(request.POST or None)
    if request.method == "POST" and form_data.is_valid():
            user = form_data.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to our store!")
            return redirect("products:home")
    
    con = {
        "data" : form_data, 
        "title" : "Create Account | ShopSphere"
    }
    return render(request, "accounts/register.html", con)



#------>User Login
def login_view(request):
    if request.user.is_authenticated: 
        return redirect("home")

    form_data = AuthenticationForm(request, request.POST or None)
    if request.method == "POST" and form_data.is_valid():
            user = form_data.get_user()
            login(request, user)

            messages.success( request, f"Welcome back, {user.first_name} {user.last_name}!" )

            next_url = request.GET.get("next") 
            if next_url: 
                return redirect(next_url) 
            
            return redirect("products:home")

    con = {
        "data" : form_data,
        "page_title" : "User Login",
        "title" : "login",
        "btn" : "Login"
    }
    return render(request, "accounts/login.html", con)



@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been loged out.')
    return redirect("products:home")



#-------->user profile
@login_required
def profile_view(request):
    user_address = AddressModel.objects.filter(user=request.user)
    form_data = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form_data.is_valid():
        form_data.save()
        messages.success(request, "profile updated.")
        return redirect("accounts:profile")


    con = {
        "data" : form_data,
        "page_title" : "User profile update",
        "title" : "My Profile | ShopSphere",
        'address' : user_address
    }
    return render(request, "accounts/profile.html", con)