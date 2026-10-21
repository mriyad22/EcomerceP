from django import forms

# This form use for taking quantity input for Product
class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,    #'min_value' is Django's validation rule
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'form':'form-control',
                'min':1     #'min' is HTML input's attribute।
            }
        )
    )


class UpdateCartItemForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'form' : 'form-control',
                'min' : 1
            }
        )
    )