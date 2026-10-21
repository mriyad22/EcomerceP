from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *
from products.models import ProductModel


#-----> Product Review View here
def add_review(request, product_id):
    product = get_object_or_404(ProductModel, id=product_id)
    review_form = ReviewForm(request.POST or None)
    if request.method == 'POST' and review_form.is_valid():
        review, created = ReviewModel.objects.update_or_create(
            user = request.user,
            product = product,
            defaults={
                'rating': review_form.cleaned_data['rating'],
                'comment': review_form.cleaned_data['comment']
            }
        )
        messages.success(request, "Review saved." if created else "Review updated." )
    return redirect('products:product_detail', slug=product.slug)