from django.urls import path
from .views import *

app_name = 'payment'

urlpatterns = [
    path('detail/<str:order_number>/', payment_detail, name='payment_detail'),
]
