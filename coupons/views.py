from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from cart.models import CartModel
from coupons.models import CouponModel
from .forms import CouponForm

#-------> Apply Coupon View here
@login_required
@require_POST
def apply_coupon(request):
    if request.method != 'POST':
        return redirect('cart:cart_detail')

    code = request.POST.get('code', '').strip().upper()
    if not code:
        messages.error(request, "Enter a coupon code.")
        return redirect("cart:cart_detail")
    
    cart, _ = CartModel.objects.get_or_create(user = request.user)

    # To find Valid Coupon from Database.
    coupon = CouponModel.objects.filter(
        code = code,
        is_active = True,
        valid_from__lte = timezone.now(),
        valid_until__gte = timezone.now()
    ).first()

    # Coupon not found?
    if not coupon:
        messages.error(request, 'Invalid or expired coupon.')
        return redirect('cart:cart_detail')

    # Verifying Coupon Usage Limits.
    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        messages.error(request, 'This coupon has reached its usage limit.')
        return redirect('cart:cart_detail')

    subtotal = cart.total_price

    # Verifying Minimum Order Amount.
    if subtotal < coupon.minimum_order_amount:
        messages.error(request, f"Minimum order amount is {coupon.minimum_order_amount}.")
        return redirect('cart:cart_detail')

    # Calculating Percentage Discount.
    discount = (subtotal * coupon.discount_percentage / Decimal('100')).quantize(Decimal('0.11'))
    if coupon.max_discount_amount is not None:
        discount = min(discount, coupon.max_discount_amount)

    # Save Coupon in Session.
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = str(discount)

    messages.success(request, f'Coupon applied. Discount: {discount}')
    return redirect('cart:cart_detail')



#------> Create Coupon View
@login_required
def add_coupon(request):
    coupon = CouponModel.objects.all()
    coupon_form = CouponForm(request.POST or None)
    if request.method == 'POST' and coupon_form.is_valid:
        coupon_form.save()
        messages.success(request, 'Coupon created.')
        return redirect('coupon:coupons')

    con = {
        'coupons' : coupon,
        'data' : coupon_form,
        'title' : 'Coupons',
        'page_title' : 'Add Coupon',
        'btn' : 'Add coupon'
    }
    return render(request,  'coupons/coupon.html', con)


#-----> Delete coupon View
@login_required
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(CouponModel, id=coupon_id)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted.')
        return redirect('coupon:coupons')

    con = {
        'object' : coupon,
        'title' : 'delete coupon',
        'coupon_page' : True
    }
    return render(request, 'delete.html', con)

