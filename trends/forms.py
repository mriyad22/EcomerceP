from django import forms
from .models import *

class TrendStuffForm(forms.ModelForm):
    class Meta:
        model = TrendStuffModel
        fields = '__all__'
