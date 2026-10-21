from django import forms
from .models import CouponModel

#-----> Discount coupon Form
class CouponForm(forms.ModelForm):
    class Meta:
        model = CouponModel
        fields = '__all__'
        exclude = ['used_count']

        widgets = {
            'valid_from':forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'}),
            'valid_until':forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'})
        }