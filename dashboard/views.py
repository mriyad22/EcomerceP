from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.db.models import Prefetch



from products.models import ProductModel, CategoryModel, BrandModel
from products.forms import ProductForm, ProductImageForm, ProductVariantForm, CategoryForm, BrandForm
from coupons.models import CouponModel
from coupons.forms import CouponForm
from orders.models import OrderModel, OrderItemModel


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
@login_required
def dashboard(request):
    if request.user.is_superuser:
        total_products = ProductModel.objects.count()
        total_categories = CategoryModel.objects.count()
        total_brands = BrandModel.objects.count()
        orders = OrderModel.objects.all()
        low_stock = ProductModel.objects.filter(stock__lte=5).order_by('stock')[:6]

        # Admin: Total Revenue
        total_revenue = orders.filter(
            payment_status=OrderModel.PaymentStatus.PAID
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

    elif request.user.is_staff:
        # Seller: Own Products
        total_products = ProductModel.objects.filter(product_owner=request.user).count()

        # Seller: Only Orders containing their products
        # 'values_list()' is used to retrieve the values ​​of specific fields only.
        seller_order_ids = OrderItemModel.objects.filter(
            product__product_owner=request.user
        ).values_list('order_id', flat=True)    #--> 'flat=True' is used to break down the inner tuples and convert the output data into a simple, flat list.
        
        """
        Here:
            1. searching for 'OrderItem' objects using `OrderItem.objects.filter()`.
            2. retrieving only those 'OrderItem' entries that belong to products owned by the currently logged-in seller, using 'product__product_owner=request.user'.
            3. collecting the 'order_id' values ​​from these 'OrderItem' entries using 'values_list('order_id', flat=True)'.
        """

        orders = OrderModel.objects.filter(pk__in=seller_order_ids)
        #--> The advantage of using 'pk__in' here is that even if an order contains multiple products from the same seller, the order will appear only once.

        # Seller: Own Low Stock Products
        low_stock = ProductModel.objects.filter(
            product_owner=request.user,
            stock__lte=5
        ).order_by('stock')[:6]

        # Seller: Revenue from own products only
        total_revenue = OrderItemModel.objects.filter(
            product__product_owner=request.user,
            order__payment_status=OrderModel.PaymentStatus.PAID
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        total_categories = None
        total_brands = None

    else:
        return HttpResponseForbidden("You don't have permission.")

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status=OrderModel.OrderStatus.PENDING).count(),
        'total_revenue': total_revenue,
        'recent_orders': orders.select_related('user').order_by('-created_at')[:5],
        'low_stock': low_stock,
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
    product = get_object_or_404(ProductModel, pk=pk) if pk else None
    form_data = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if not pk:
        if request.method == 'POST' and form_data.is_valid():
            product = form_data.save(commit=False)
            product.product_owner = request.user
            product.save()
            messages.success(request, 'Product saved successfully.')
            return redirect('dashboard:products')

    elif pk:
        if request.method == 'POST':
            action = request.POST.get('action', 'product')
    
            if action == 'product' and form_data.is_valid():
                form_data.save()
                messages.success(request, 'Product updated.')
                return redirect('dashboard:products')
    
            if action == 'image':
                image_form = ProductImageForm(request.POST, request.FILES)
                if image_form.is_valid():
                    image = image_form.save(commit=False)
                    image.product = product
                    image.save()
                    messages.success(request, 'Gallery image added.')
                    return redirect('dashboard:products')
    
            if action == 'variant':
                variant_form = ProductVariantForm(request.POST, request.FILES)
                if variant_form.is_valid():
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()
                    messages.success(request, 'Product variant added.')
                    return redirect('dashboard:products')
                
    image_form = ProductImageForm()
    variant_form = ProductVariantForm()

    context =  {
        'form': form_data, 
        'page_title': 'Edit product' if product else 'Add product', 
        'cancel_url': 'dashboard:products',
        'product_data' : form_data,
        'image_data' : image_form,
        'variant_data' : variant_form,
        'product' : product,
        'title' : 'Edit product',
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


#----> Dynamic create update View for Category and brand.
def _catalog_page(request, model, form_class, template_title, list_name, pk=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{template_title[:-1] if template_title.endswith("s") else template_title} saved successfully.')
        return redirect(f'dashboard:{list_name}')
    items = model.objects.all().order_by('-id')

    context = {
        'form': form, 
        'items': items, 
        'page_title': f'Edit {template_title[:-1].lower()}' if instance else f'Add {template_title[:-1].lower()}', 
        'list_title': template_title, 
        'list_name': list_name, 
        'list_url': f'dashboard:{list_name}', 'edit_route': f'dashboard:{list_name}_edit', 
        'delete_route': f'dashboard:{list_name}_delete'
    }
    return render(request, 'dashboard/catalog.html', context)


#-------->Create Category create View
@staff_required
def categories(request):
    return _catalog_page(request, CategoryModel, CategoryForm, 'Categories', 'categories')


#-------->Update Category View
@staff_required
def category_edit(request, pk):
    return _catalog_page(request, CategoryModel, CategoryForm, 'Categories', 'categories', pk)


#--------> Delete category Veiw
@staff_required
@require_POST
def category_delete(request, pk):
    get_object_or_404(CategoryModel, pk=pk).delete()
    messages.success(request, 'Category deleted.')
    return redirect('dashboard:categories')


#-------> Create brand View
@staff_required
def brands(request):
    return _catalog_page(request, BrandModel, BrandForm, 'Brands', 'brands')


#--------> Update brand View
@staff_required
def brand_edit(request, pk):
    return _catalog_page(request, BrandModel, BrandForm, 'Brands', 'brands', pk)


#--------> Delete brand View
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
    seller_order_ids = OrderItemModel.objects.filter(
        product__product_owner = request.user
    ).values_list('order_id', flat=True)

    if request.user.is_superuser:
        qs = OrderModel.objects.select_related('user').order_by('-created_at')

    elif request.user.is_staff:
        qs = OrderModel.objects.filter(pk__in = seller_order_ids).select_related('user').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    if query:
        qs = qs.filter(
            Q(order_number__icontains=query) | 
            Q(full_name__icontains=query) | 
            Q(phone__icontains=query)
        )
        
    valid_statuses = {value for value, label in OrderModel.OrderStatus.choices}
    if status in valid_statuses:
        qs = qs.filter(status=status)
        
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj, 
        'query': query, 
        'selected_status': status, 
        'statuses': OrderModel.OrderStatus.choices
    }
    return render(request, 'dashboard/orders.html', context)


#------> Product order detail View
@staff_required
def order_detail(request, order_number):

    # Admin: All Order Items
    if request.user.is_superuser:
        order_queryset = OrderModel.objects.select_related(
            'user', 'coupon'
        ).prefetch_related('order_items__product')

    # Seller: Only Own Product Orders
    else:
        order_queryset = OrderModel.objects.select_related(
            'user', 'coupon'
        ).filter(
            order_items__product__product_owner=request.user
        ).distinct().prefetch_related(
            Prefetch(
                'order_items',
                queryset=OrderItemModel.objects.filter(
                    product__product_owner=request.user
                ).select_related('product'),
                to_attr='seller_order_items'
            )
        )

    # Get Order
    order = get_object_or_404(order_queryset, order_number=order_number)

    # Get Order Items
    if request.user.is_superuser:
        order_items = order.order_items.all()
    else:
        order_items = order.seller_order_items

    # Update Order Status (Admin Only)
    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponseForbidden(
                "You don't have permission to update this order."
            )

        status = request.POST.get('status')
        payment_status = request.POST.get('payment_status')

        valid_order = {v for v, _ in OrderModel.OrderStatus.choices}
        valid_payment = {v for v, _ in OrderModel.PaymentStatus.choices}

        if status in valid_order and payment_status in valid_payment:
            order.status = status
            order.payment_status = payment_status
            order.save(
                update_fields=[
                    'status',
                    'payment_status',
                    'updated_at'
                ]
            )
            messages.success(request, 'Order status updated.')
            return redirect('dashboard:order_detail', order_number=order.order_number)

        messages.error(request, 'Please choose valid order and payment statuses.')

    context = {
        'order': order,
        'order_items': order_items,
        'order_statuses': OrderModel.OrderStatus.choices,
        'payment_statuses': OrderModel.PaymentStatus.choices,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'dashboard/order_detail.html', context)








#------> Download order list pdf

from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


from xml.sax.saxutils import escape


@staff_required
def download_order_pdf(request, order_number):

    is_admin = request.user.is_superuser

    # --------------------------------
    # Get Order Based on User Role
    # --------------------------------

    if is_admin:
        order_queryset = OrderModel.objects.select_related(
            'user', 'coupon'
        ).prefetch_related(
            'order_items__product'
        )

    else:
        order_queryset = OrderModel.objects.filter(
            order_items__product__product_owner=request.user
        ).distinct().select_related(
            'user', 'coupon'
        ).prefetch_related(
            'order_items__product'
        )

    order = get_object_or_404(
        order_queryset,
        order_number=order_number
    )

    # --------------------------------
    # Filter Order Items
    # --------------------------------

    if is_admin:
        order_items = order.order_items.all()
    else:
        order_items = order.order_items.filter(
            product__product_owner=request.user
        )

    # Seller's Own Subtotal
    seller_subtotal = sum((item.total_price for item in order_items), 0)

    # --------------------------------
    # Create PDF Buffer
    # --------------------------------

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ShopTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor('#2563EB'),
        alignment=TA_LEFT,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#172554'),
        spaceBefore=12,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
    ))

    elements = []

    # --------------------------------
    # Header
    # --------------------------------

    elements.append(Paragraph('ShopSphere', styles['ShopTitle']))
    elements.append(
        Paragraph(
            'Order Details / Seller Invoice',
            styles['Heading2']
        )
    )

    elements.append(Spacer(1, 5 * mm))

    # --------------------------------
    # Order Information
    # --------------------------------
    elements.append( Paragraph('Order Information', styles['SectionHeading']))
    created_at = timezone.localtime(order.created_at)
    order_info = [
        ['Order Number', escape(str(order.order_number))],
        ['Order Date', created_at.strftime('%d %B %Y, %I:%M %p')],
        ['Order Status', escape(str(order.get_status_display()))],
        ['Payment Status', escape(str(order.get_payment_status_display()))],
    ]

    info_table = Table(
        order_info,
        colWidths=[45 * mm, 120 * mm]
    )

    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EFF6FF')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1E40AF')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(info_table)

    # --------------------------------
    # Customer Information
    # --------------------------------

    elements.append(
        Paragraph('Customer Information', styles['SectionHeading'])
    )

    customer_info = [
        ['Full Name', escape(str(order.full_name))],
        ['Phone', escape(str(order.phone))],
        ['Address', escape(str(order.address))],
        ['City', escape(str(order.city))],
        ['Country', escape(str(order.country))],
    ]

    customer_table = Table(
        customer_info,
        colWidths=[45 * mm, 120 * mm]
    )

    customer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(customer_table)

    # --------------------------------
    # Product Information
    # --------------------------------

    elements.append(
        Paragraph('Products in this Order', styles['SectionHeading'])
    )

    product_data = [
        ['Product', 'Unit Price', 'Qty', 'Total']
    ]

    for item in order_items:
        product_data.append([
            Paragraph(
                escape(str(item.product_name)),
                styles['SmallText']
            ),
            f'BDT {item.price:,.2f}',
            str(item.quantity),
            f'BDT {item.total_price:,.2f}',
        ])

    product_table = Table(
        product_data,
        colWidths=[
            75 * mm,
            32 * mm,
            18 * mm,
            40 * mm
        ],
        repeatRows=1
    )

    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor('#F8FAFC')
        ]),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(product_table)

    # --------------------------------
    # Total Calculation
    # --------------------------------

    elements.append(Spacer(1, 6 * mm))

    if is_admin:
        totals = [
            ['Subtotal', f'BDT {order.subtotal:,.2f}'],
            ['Shipping', f'BDT {order.shipping_cost:,.2f}'],
            ['Discount', f'BDT {order.discount:,.2f}'],
            ['Grand Total', f'BDT {order.total_amount:,.2f}'],
        ]
    else:
        # Seller cannot see complete order total
        totals = [
            ['Your Product Subtotal', f'BDT {seller_subtotal:,.2f}'],
        ]

    total_table = Table(totals, colWidths=[125 * mm, 40 * mm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2563EB')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(total_table)

    # --------------------------------
    # Seller Information
    # --------------------------------

    if not is_admin:
        elements.append(Spacer(1, 8 * mm))
        seller_name = (
            request.user.get_full_name()
            or request.user.username
        )

        elements.append(
            Paragraph(
                f'Seller: {escape(seller_name)}',
                styles['SmallText']
            )
        )

    # --------------------------------
    # Footer
    # --------------------------------

    elements.append(Spacer(1, 15 * mm))
    elements.append(
        Paragraph(
            'Thank you for using ShopSphere.',
            ParagraphStyle(
                name='Footer',
                parent=styles['Normal'],
                alignment=TA_CENTER,
                fontSize=9,
                textColor=colors.grey,
            )
        )
    )

    # --------------------------------
    # Generate PDF
    # --------------------------------

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="Order_{order.order_number}.pdf"'
    )

    return response
