from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
import uuid

from .forms import *
from .models import *
from cart.models import CartModel
from coupons.models import CouponModel
from payments.models import PaymentModel


#----> Order Checkout View
def checkout_view(request):
    cart, _ = CartModel.objects.get_or_create(user=request.user)
    items = list(cart.cart_items.select_related('product', 'variant'))
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    addresses = AddressModel.objects.filter(user=request.user)
    address_form = AddressForm(request.POST or None)

    subtotal = cart.total_price
    shipping = Decimal('100') if subtotal < Decimal('5000') else Decimal('0.00')
    discount = Decimal(request.session.get('coupon_discount', '0'))
    discount = min(discount, subtotal)  #Ensure that the discount is not greater than the subtotal.| min() returns the smaller of two values.
    coupon_code = request.session.get('coupon_code')
    coupon = CouponModel.objects.filter(code=coupon_code, is_active=True).first() if coupon_code else None
    total = subtotal + shipping - discount

    if request.method ==  'POST' and address_form.is_valid():
        with transaction.atomic():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()

            # Re-check stock inside the transaction.
            for item in items:
                stock = item.variant.stock if item.variant else item.product.stock
                if item.quantity > stock:
                    messages.error(request, f'Not enough stock for {item.product.name}.')
                    return redirect('cart:cart_detail')

            #---> Create Order Model
            order = OrderModel.objects.create(
                user = request.user,
                order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}",
                coupon = coupon,
                full_name = address.full_name,
                phone = address.phone,
                address = address.address_line,
                city = address.city,
                country=address.country,
                subtotal = subtotal,
                shipping_cost = shipping,
                discount = discount,
                total_amount = total,
            )

            #---> Create order item Model
            for item in items:
                unit_price = item.unit_price
                OrderItemModel.objects.create(
                    order = order,
                    product = item.product,
                    variant = item.variant,
                    product_name = item.product.name,
                    price = unit_price,
                    quantity = item.quantity,
                    total_price = unit_price * item.quantity,
                )

                if item.variant:
                    item.variant.stock -= item.quantity
                    item.variant.save(update_fields=[stock])
                else:
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

            #---> Create payment model
            PaymentModel.objects.create(
                order = order,
                user = request.user,
                amount = total,
                method = PaymentModel.PAYMENT_METHOD[0][0],
                status = PaymentModel.PaymentStatus.PENDING
            )

            #---> Increasing the number of coupon uses
            if coupon:
                coupon.used_count += 1
                coupon.save(update_fields=["used_count"])

            cart.cart_items.all().delete()
            request.session.pop("coupon_code", None)
            request.session.pop("coupon_discount", None)

        messages.success(request, 'Order plased successfully.')
        return redirect("order:order_detail", order_number=order.order_number)

    con = {
        'cart' : cart,
        'items' : items,
        'addresses' : addresses,
        'address_form' :address_form,
        'subtotal' : subtotal,
        'shipping' : shipping,
        'discount' : discount,
        'total' : total
    }
    return render(request, 'order/checkout.html', con)





#--------> Order List View 
def order_list(request):
    orders = OrderModel.objects.filter(user=request.user).order_by('-created_at')

    con = {
        'orders' : orders
    }
    return render(request, 'order/order_list.html', con)




#------> Order Detail View
def order_detail(request, order_number):
    order = get_object_or_404(
        OrderModel.objects.prefetch_related('order_items'),
        order_number = order_number,
        user = request.user
    )

    con = {
        'order' : order
    }
    return render(request, 'order/order_detail.html', con)




#--------> Create Address  View
def address_create(request):
    try:
        address = request.user.user_address
    except AddressModel.DoesNotExist:
        address = None
    address_form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST' and address_form.is_valid():
        address = address_form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, 'Address saved.')
        return redirect('accounts:profile')

    con = {
        'form' : address_form
    }
    return render(request, 'order/address_form.html', con)