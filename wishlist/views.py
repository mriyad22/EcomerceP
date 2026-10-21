from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import *
from .forms import *
from products.models import ProductModel


#-----> Wishlist detail View
@login_required
def wishlist_detail(request):
    wishlist, _ = WishlistModel.objects.get_or_create(user=request.user)

    con = {
        'wishlist' : wishlist
    }
    return render(request, 'wishlist/wishlist_detail.html', con)



# -------> Wishlist item View
@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(ProductModel, id = product_id)
    wishlist, _ = WishlistModel.objects.get_or_create(user=request.user)
    item, created = WishlistItemModel.objects.get_or_create(wishlist=wishlist, product=product)
    if not created:
        item.delete()
        messages.info(request, 'Removed from wishlist.')
    else:
        messages.success(request, 'Added to wishlist.')
    return redirect(request.META.get("HTTP_REFERER", "products:product_list"))


"""
1. What is request.META?

It is a dictionary that stores information regarding the user's browser, IP address, request method (GET/POST),
and headers. For example, it contains the following:
    • request.META['REMOTE_ADDR'] — The user's IP address.
    • request.META['HTTP_USER_AGENT'] — The browser or mobile device the user is using.
    • request.META['HTTP_REFERER'] — The specific page from which the user arrived by clicking a link.
"""