from django.urls import path
from .views import *

app_name = 'cart'


urlpatterns = [
    #-----> cart urls
    path('', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('order-now/<int:product_id>/', order_now, name='order_now'),
    path('update/<int:item_id>/', update_cart_item, name='update_item'),
    path('remove/<int:item_id>/', remove_cart_item, name='remove_item')
]
