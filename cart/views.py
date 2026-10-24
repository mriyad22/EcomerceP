from django.shortcuts import render, redirect, get_object_or_404
from products.models import ProductModel, ProductVariantModel
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *


#-------> Cart detail View
@login_required
def cart_detail(request):
    cart, _ = CartModel.objects.get_or_create(user=request.user)
    items = cart.cart_items.select_related('product', 'variant')

    con = {
        'cart' : cart,
        'items' : items
    }
    return render(request, 'cart/cart_detail.html', con)


#--------> Create item to cart View
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(ProductModel, id = product_id, is_available = True)
    form_data = AddToCartForm(request.POST or None)

    # product variant
    variant = None
    variant_id = request.POST.get('variant')
    if variant_id:
        variant = get_object_or_404(ProductVariantModel, id = variant_id, product=product)

    if request.method == 'POST' and form_data.is_valid():
        #check quantity is available
        quantity = form_data.cleaned_data['quantity']
        available_stock = variant.stock if variant else product.stock
        if quantity > available_stock:
            messages.error(request, 'Not enough stock available.')
            return redirect('products:product_detail')

        #Create cart item
        cart, _ = CartModel.objects.get_or_create(user = request.user)
        item, created = CartItemModel.objects.get_or_create(cart=cart, product=product, variant=variant)
        new_quantity = quantity if created else item.quantity + quantity
        if new_quantity > available_stock:
            messages.error(request, 'Requested quantity exceeds available stock.')
        else:
            item.quantity = new_quantity
            item.save()
            messages.success(request, 'Product added to cart.')
        return redirect('cart:cart_detail')
    return redirect('products:product_detail', slug=product.slug)   # 'slug' It can take you back to the detail page of the product you were viewing.


#--------> Order Now View
def order_now(request, product_id):
    product = get_object_or_404(ProductModel, id=product_id, is_available=True)

    if request.method != 'POST':
        return redirect("products:product_detail", slug=product.slug)

    form_data = AddToCartForm(request.POST)
    variant = None
    variant_id = request.POST.get('variant')
    if variant_id:
        variant = get_object_or_404(ProductVariantModel, id = variant_id, product=product, is_active=True)

    if not form_data.is_valid():
        messages.error(request, 'Please enter a valid quantity.')
        return redirect("products:product_detail", slug=product.slug)

    quantity = form_data.cleaned_data['quantity']
    available_stock = variant.stock if variant else product.stock
    if quantity > available_stock:
        messages.error(request, 'Not enough stock available.')
        return redirect('products:product_detail')

    # Store only the selected product details in the session.
    request.session['order_now'] = {
        'product_id' : product.pk,
        'variant_id' : variant.pk if variant else None,
        'quantity' : quantity
    }
    return redirect('order:checkout')


#------> Cart update item View
@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItemModel, id=item_id, cart__user=request.user)
    form_data = UpdateCartItemForm(request.POST or None)
    if request.method == 'POST' and form_data.is_valid():
        quantity = form_data.cleaned_data['quantity']
        stock = item.variant.stock if item.variant else item.product.stock
        if quantity <= stock:
            item.quantity = quantity
            item.save()
            messages.success(request, 'Cart updated.')
        else:
            messages.error(request, 'Quantity exceeds stock.')

        return redirect('cart:cart_detail')



#-----> Remove cart item View
@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItemModel, id = item_id, cart__user=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Remove item')
    return redirect('cart:cart_detail')

    
    