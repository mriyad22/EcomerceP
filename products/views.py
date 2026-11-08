from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.paginator import Paginator

from .forms import *
from .models import *
from trends.models import TrendStuffModel

from django.db.models import Q


#------> Product home view
def home(request):
    trends = TrendStuffModel.objects.filter(is_active=True).order_by('-created_at')
    
    caegories = CategoryModel.objects.filter(is_active=True)
    if request.user.is_authenticated:
        if not request.user.is_customer:
            featured = ProductModel.objects.filter(is_featured=True, is_available=True, product_owner=request.user).select_related('category', 'brand')[:8]
            latest = ProductModel.objects.filter(is_available=True, product_owner=request.user).select_related('category', 'brand')[:12]
        else:
            featured = ProductModel.objects.filter(is_featured=True, is_available=True).select_related('category', 'brand')[:8]
            latest = ProductModel.objects.filter(is_available=True).select_related('category', 'brand')[:12]
    else:
        featured = ProductModel.objects.filter(is_featured=True, is_available=True).select_related('category', 'brand')[:8]
        latest = ProductModel.objects.filter(is_available=True).select_related('category', 'brand')[:12]

    con = {
        'categories' : caegories,
        'featured' : featured,
        'latest' : latest,
        'trends' : trends
    }
    return render(request, 'product/home.html', con)



#---------> Product Create View here
@login_required
def product_create(request):
    if request.user.is_customer:
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
    form_data = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form_data.is_valid():
        product = form_data.save(commit=False)
        product.product_owner = request.user
        product.save()
        messages.success(request, 'Product created.')
        return redirect('products:home')

    con = {
        'product_data' : form_data,
        'title' : 'Add Product',
        'product_btn' : 'Save product'
    }
    return render(request, 'product/product_form.html', con)



#--------> Product list view
def product_list(request):
    if request.user.is_authenticated:
        if not request.user.is_customer:
            products = ProductModel.objects.filter(is_available = True, product_owner=request.user).select_related('category', 'brand').order_by('-id')
        else:
            products = ProductModel.objects.filter(is_available = True).select_related('category', 'brand').order_by('-id')
    else:
        products = ProductModel.objects.filter(is_available = True).select_related('category', 'brand').order_by('-id')
        
    categories = CategoryModel.objects.filter(is_active = True)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('categoryx', '').strip()
    sort = request.GET.get('sort', '').strip()

    #--> Search functionality
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    if category:
        products = products.filter(category__slug=category)

    if sort == 'new':
        products = products.order_by('-created_at')
    elif sort == 'low':
        products = products.order_by('price')
    elif sort == 'high':
        products = products.order_by('-price')

    #--> Pagination
    paginator = Paginator(products, 18)
    page_obj = paginator.get_page(request.GET.get('page'))


    con = {
        'categories' : categories,
        'query' : query,
        'selected_category' : category,
        'selected_sort' : sort,
        'page_obj' : page_obj
    }
    return render(request, 'product/product_list.html', con)



#--------> Product detail view
def product_detail(request, slug):
    product = get_object_or_404(
        ProductModel.objects.select_related('category', 'brand').prefetch_related('product_images', 'product_variants', 'product_reviews__user'),
        slug = slug,
        is_available = True
    )

    con = {
        'product' : product
    }
    return render(request, 'product/product_detail.html', con)




#--------> Product Edit view
@login_required
def product_edit(request, e_id):
    if request.user.is_customer:
        messages.warning(request, "You don't have permission here")
        return redirect('products:home')
    
    product = get_object_or_404(ProductModel, id = e_id)
    form_data = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST':
        action = request.POST.get('action', 'product')

        if action == 'product' and form_data.is_valid():
            form_data.save()
            messages.success(request, 'Product updated.')
            return redirect('products:product_list')

        if action == 'image':
            image_form = ProductImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.product = product
                image.save()
                messages.success(request, 'Gallery image added.')
                return redirect('products:product_list')

        if action == 'variant':
            variant_form = ProductVariantForm(request.POST, request.FILES)
            if variant_form.is_valid():
                variant = variant_form.save(commit=False)
                variant.product = product
                variant.save()
                messages.success(request, 'Product variant added.')
                return redirect('products:product_list')
            
    image_form = ProductImageForm()
    variant_form = ProductVariantForm()
    con = {
        'product_data' : form_data,
        'image_data' : image_form,
        'variant_data' : variant_form,
        'product' : product,
        'title' : 'Edit product',
        'product_btn' : 'Update product'
    }
    return render(request, 'product/product_form.html', con)
