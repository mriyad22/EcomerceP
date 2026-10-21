from django.urls import path
from .views import *

app_name = 'coupon'

urlpatterns = [
    path('apply/', apply_coupon, name='apply_coupon'),
    path('', add_coupon, name='coupons'),
    path('delete/<int:coupon_id>/', delete_coupon, name='delete_coupon'),
]
