from django.urls import path
from .views import *

app_name = 'products'

urlpatterns = [
    path('', home, name='home'),

    #---------> Product URLs
    path('products/product-create/', product_create, name='product_create'),
    path('products/', product_list, name='product_list'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('products/<int:e_id>/edit/', product_edit, name='product_edit'),

]
