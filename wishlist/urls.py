from django.urls import path
from .views import *

app_name = 'wishlist'

urlpatterns = [
    path('detail/', wishlist_detail, name='wishlist_detail'),
    path('toggle/<int:product_id>/', toggle_wishlist, name='toggle'),
]
