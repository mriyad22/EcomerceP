from django.urls import path
from .views import *

app_name = 'trends'

urlpatterns = [
    path('trends/', create_trend, name='trend'),
    path('edit-trend/<int:edit_id>/', edit_trend, name='edit_trend'),
    path('delete_trend/<int:delete_id>/', delete_trend, name='delete_trend'),
]
