from django.urls import path
from .views import *

urlpatterns = [
    path('trend-Stuff/', create_trend_stuff, name='trend'),
]
