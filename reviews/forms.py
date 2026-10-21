from django import forms
from .models import ReviewModel

#-----> Review Form here
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ('rating', 'comment')
        exclude = ['user', 'product', 'is_verified_purchase']

        widgets = {
            'rating':forms.Select(
                choices=[(5, '5 - Excellent'), (4, '4 - Very Good'), (3, '3 - Good'), (2, '2 - Fair'), (1, '1 - Poor')]
            ),
            'comment':forms.Textarea(attrs={"class":"form-control", "rows":4})
        }