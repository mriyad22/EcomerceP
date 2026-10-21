from django import forms
from .models import *

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressModel
        fields = '__all__'
        exclude = ['user']

    widgets = {
        'address_line':forms.Textarea(attrs={"class":"form-control", "rows":4})
    }