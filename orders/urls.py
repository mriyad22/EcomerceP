from django.urls import path
from .views import *

app_name = 'order'

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('', order_list, name='order_list'),
    path('<str:order_number>/', order_detail, name='order_detail'),
    path('address/add/', address_create, name='address_create'),
]
