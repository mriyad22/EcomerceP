from django.urls import path
from .views import *

app_name = 'trends'

urlpatterns = [
    path('trends/', create_trend_stuff, name='trend'),
    path('edit-trend/<int:edit_id>/', edit_trend_stuff, name='edit_trend'),
    path('delete_trend/<int:delete_id>/', delete_trend, name='delete_trend'),
]
