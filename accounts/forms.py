from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AuthUserModel


#-------> Registation form
class UserRegistationForm(UserCreationForm):
    class Meta: 
        model = AuthUserModel
        fields = [
            "username",
            "email", 
            "password1",
            "password2",
            "is_customer"
        ]



#-------> Profile update form
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AuthUserModel
        fields = [
            "first_name", 
            "last_name", 
            "email", 
            "phone", 
            "profile_image"
        ]