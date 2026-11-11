from django.urls import path
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),

    #-------> Products CRUD operation url
    path('dashboard/products/', product_list, name='products'),
    path('dashboard/products/add/', product_form, name='product_add'),
    path('dashboard/products/<int:pk>/edit/', product_form, name='product_edit'),
    path('dashboard/products/<int:pk>/delete/', product_delete, name='product_delete'),

    #-------> Product categories url
    path('dashboard/categories/', categories, name='categories'),
    path('dashboard/categories/<int:pk>/edit/', category_edit, name='categories_edit'),
    path('dashboard/categories/<int:pk>/delete/', category_delete, name='categories_delete'),

    #-------> Product brands url
    path('dashboard/brands/', brands, name='brands'),
    path('dashboard/brands/<int:pk>/edit/', brand_edit, name='brands_edit'),
    path('dashboard/brands/<int:pk>/delete/', brand_delete, name='brands_delete'),

    #-------> Coupon url
    path('dashboard/coupons/', coupons, name='coupons'),
    path('dashboard/coupons/<int:pk>/delete/', coupon_delete, name='coupon_delete'),

    #-------> Product orders url
    path('dashboard/orders/', order_list, name='orders'),
    path('dashboard/orders/<str:order_number>/', order_detail, name='order_detail'),

    #-------> Download order report url
    path('orders/<str:order_number>/download/', download_order_pdf, name='download_order_pdf'),
]
