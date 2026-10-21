from django.urls import path
from .views import *

app_name = 'products'

urlpatterns = [
    path('', home, name='home'),
    
    #------> product category urls here
    path('products/categories/', product_category, name='product_category'),
    path('products/category-edit/<int:e_id>/', product_category_edit, name='product_category_edit'),
    path('products/category-delete/<int:d_id>/', product_category_delete, name='product_category_delete'),

    #-------> product brand urls
    path('products/brands/', product_brand, name='product_brand'),
    path('products/brand-edit/<int:e_id>/', product_brand_edit, name='product_brand_edit'),
    path('products/brand-delete/<int:d_id>/', product_brand_delete, name='product_brand_delete'),

    #---------> Product URLs
    path('products/product-create/', product_create, name='product_create'),
    path('products/', product_list, name='product_list'),
    path('products/<slug:slug>/', product_detail, name='product_detail'),
    path('products/<int:e_id>/edit/', product_edit, name='product_edit'),

]
