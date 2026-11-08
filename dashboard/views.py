from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import ProductModel, CategoryModel, BrandModel
from products.forms import ProductForm, CategoryForm, BrandForm
from coupons.models import CouponModel
from coupons.forms import CouponForm
from orders.models import OrderModel


#----> create a staff decorator
def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('products:home')
        return view_func(request, *args, **kwargs)
    return wrapper


#-------> Dashboard View
@staff_required
def dashboard(request):
    orders = OrderModel.objects.all()
    context = {
        'total_products': ProductModel.objects.count(),
        'total_categories': CategoryModel.objects.count(),
        'total_brands': BrandModel.objects.count(),
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status=OrderModel.OrderStatus.PENDING).count(),
        'total_revenue': orders.filter(payment_status=OrderModel.PaymentStatus.PAID).aggregate(total=Sum('total_amount'))['total'] or 0,
        'recent_orders': orders.select_related('user').order_by('-created_at')[:8],
        'low_stock': ProductModel.objects.filter(stock__lte=5).order_by('stock')[:6],
    }
    return render(request, 'dashboard/index.html', context)


#------> Product List View
@staff_required
def product_list(request):
    qs = ProductModel.objects.select_related('category', 'brand').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(category__name__icontains=query)
        )

    page_obj = Paginator(qs, 12).get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj, 
        'query': query
    }
    return render(request, 'dashboard/product_list.html', context)



#-----> Product add and edit View
@staff_required
def product_form(request, pk=None):
    instance = get_object_or_404(ProductModel, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        if not product.pk:
            product.product_owner = request.user
        product.save()
        messages.success(request, 'Product saved successfully.')
        return redirect('dashboard:products')
    
    context =  {
        'form': form, 
        'page_title': 'Edit product' if instance else 'Add product', 
        'cancel_url': 'dashboard:products'
    }
    return render(request, 'dashboard/form.html', context)


#-------> Product delete Veiw
@staff_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(ProductModel, pk=pk)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('dashboard:products')


def _catalog_page(request, model, form_class, template_title, list_name, pk=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{template_title[:-1] if template_title.endswith("s") else template_title} saved successfully.')
        return redirect(f'dashboard:{list_name}')
    items = model.objects.all().order_by('-id')
    return render(request, 'dashboard/catalog.html', {'form': form, 'items': items, 'page_title': f'Edit {template_title[:-1].lower()}' if instance else f'Add {template_title[:-1].lower()}', 'list_title': template_title, 'list_name': list_name, 'list_url': f'dashboard:{list_name}', 'edit_route': f'dashboard:{list_name}_edit', 'delete_route': f'dashboard:{list_name}_delete'})


@staff_required
def categories(request):
    return _catalog_page(request, CategoryModel, CategoryForm, 'Categories', 'categories')


@staff_required
def category_edit(request, pk):
    return _catalog_page(request, CategoryModel, CategoryForm, 'Categories', 'categories', pk)


@staff_required
@require_POST
def category_delete(request, pk):
    get_object_or_404(CategoryModel, pk=pk).delete()
    messages.success(request, 'Category deleted.')
    return redirect('dashboard:categories')


@staff_required
def brands(request):
    return _catalog_page(request, BrandModel, BrandForm, 'Brands', 'brands')


@staff_required
def brand_edit(request, pk):
    return _catalog_page(request, BrandModel, BrandForm, 'Brands', 'brands', pk)


@staff_required
@require_POST
def brand_delete(request, pk):
    get_object_or_404(BrandModel, pk=pk).delete()
    messages.success(request, 'Brand deleted.')
    return redirect('dashboard:brands')

#---------> Create a coupon View
@staff_required
def coupons(request):
    form = CouponForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Coupon created successfully.')
        return redirect('dashboard:coupons')
    items = CouponModel.objects.order_by('-created_at')

    context = {
        'form': form, 
        'coupons': items
    }
    return render(request, 'dashboard/coupons.html', context)


#--------> Delete coupon View
@staff_required
@require_POST
def coupon_delete(request, pk):
    get_object_or_404(CouponModel, pk=pk).delete()
    messages.success(request, 'Coupon deleted.')
    return redirect('dashboard:coupons')



#---------> Product order list Veiw
@staff_required
def order_list(request):
    qs = OrderModel.objects.select_related('user').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    if q:
        qs = qs.filter(Q(order_number__icontains=q) | Q(full_name__icontains=q) | Q(phone__icontains=q))
    valid_statuses = {value for value, label in OrderModel.OrderStatus.choices}
    if status in valid_statuses:
        qs = qs.filter(status=status)
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj, 
        'query': q, 
        'selected_status': status, 
        'statuses': OrderModel.OrderStatus.choices
    }
    return render(request, 'dashboard/orders.html', context)


#------> Product order detail View
@staff_required
def order_detail(request, order_number):
    order = get_object_or_404(
        OrderModel.objects.select_related('user', 'coupon').prefetch_related('order_items__product'), 
        order_number=order_number
    )
    
    if request.method == 'POST':
        status = request.POST.get('status')
        payment_status = request.POST.get('payment_status')
        valid_order = {v for v, _ in OrderModel.OrderStatus.choices}
        valid_payment = {v for v, _ in OrderModel.PaymentStatus.choices}
        if status in valid_order and payment_status in valid_payment:
            order.status = status
            order.payment_status = payment_status
            order.save(update_fields=['status', 'payment_status', 'updated_at'])
            messages.success(request, 'Order status updated.')
            return redirect('dashboard:order_detail', order_number=order.order_number)
        messages.error(request, 'Please choose valid order and payment statuses.')

    context = {
        'order': order, 
        'order_statuses': OrderModel.OrderStatus.choices, 
        'payment_statuses': OrderModel.PaymentStatus.choices
    }
    return render(request, 'dashboard/d_order_detail.html', context)
