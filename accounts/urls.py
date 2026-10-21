from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    #------> User authentication url
    path("register/", register_view, name="register"), 
    path("login/", login_view, name="login"), 
    path("logout/", logout_view, name="logout"),

    #------> User profile url
    path('profile/', profile_view, name="profile"),
]
