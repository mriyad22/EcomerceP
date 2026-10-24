from django import forms
from .models import *

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressModel
        fields = '__all__'
        exclude = ['user']

    # if use 'CRISPY' in template and wanna modify any field.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'address_line' in self.fields:
            self.fields['address_line'].widget.attrs.update({'rows':4})