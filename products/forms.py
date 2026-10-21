from django import forms
from .models import *

#----> Product Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryModel
        fields = '__all__'


#--------> Product Brand Form
class BrandForm(forms.ModelForm):
    class Meta:
        model = BrandModel
        fields = '__all__'



#-------> Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = '__all__'
        exclude = [
            'product_owner',
            'created_at',
            'updated_at'
        ]



#-------> Product Image Form
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImageModel
        fields = '__all__'
        exclude = [
            'product',
            'created_at',
            'updated_at'
        ]



#-------> Product Variant Form
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariantModel
        fields = '__all__'
        exclude = [
            'product'
        ]