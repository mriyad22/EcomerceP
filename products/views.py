from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import *

from django.db.models import Q


#------> Product home view
def home(request):
    categories = CategoryModel.objects.filter(is_active=True)
    featured = ProductModel.objects.filter(is_featured=True, is_available=True).select_related('category', 'brand')[:8]
    latest = ProductModel.objects.filter(is_available=True).select_related('category', 'brand')[:12]

    con = {
        'categories' : categories,
        'featured' : featured,
        'latest' : latest
    }
    return render(request, 'product/home.html', con)


#------> Product category View
def product_category(request):
    categories = CategoryModel.objects.all()
    form_data = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'Category created.')
        return redirect('products:product_category')

    con = {
        'data' : form_data,
        'categories' : categories,
        'title' : 'Categories | ShopSphere',
        'page_title' : 'Add category',
        'btn' : 'Create category'
    }
    return render(request, 'product/product_category.html', con)



#--------> product category Update view
def product_category_edit(request, e_id):
    category = get_object_or_404(CategoryModel, id = e_id)
    form_data = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'Category updated.')
        return redirect('products:product_category')

    con = {
        'data' : form_data,
        'title' : 'Category updated.',
        'page_title' : 'Edit category',
        'btn' : 'Update'
    }
    return render(request, 'product/product_category.html', con)



#--------> product category Delete view
def product_category_delete(request, d_id):
    category_del = get_object_or_404(CategoryModel, id = d_id)
    if request.method == 'POST':
        category_del.delete()
        messages.success(request, 'Category deleted.')
        return redirect('products:product_category')

    con = {
        'title' : 'Category delete',
        'object' : category_del,
        'category_page' : True
    }
    return render(request, 'delete.html', con)




#-------> Product Brand view
def product_brand(request):
    brands = BrandModel.objects.all()

    form_data = BrandForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'Brand created.')
        return redirect('products:product_brand')

    con = {
        'data' : form_data,
        'brands' : brands,
        'page_title' : 'Add brand',
        'title' : 'Brands | ShopSphere',
        'btn' : 'Create brand'
    }
    return render(request, 'product/product_brand.html', con)




#--------> product brand Update view
def product_brand_edit(request, e_id):
    brand = get_object_or_404(BrandModel, id = e_id)
    form_data = BrandForm(request.POST or None, request.FILES or None, instance=brand)
    if request.method == 'POST' and form_data.is_valid():
        form_data.save()
        messages.success(request, 'brand updated.')
        return redirect('products:product_brand')

    con = {
        'data' : form_data,
        'title' : 'brand updated.',
        'page_title' : 'Edit brand',
        'btn' : 'Update'
    }
    return render(request, 'product/product_brand.html', con)



#--------> product brand Delete view
def product_brand_delete(request, d_id):
    brand_del = get_object_or_404(BrandModel, id = d_id)
    if request.method == 'POST':
        brand_del.delete()
        messages.success(request, 'brand deleted.')
        return redirect('products:product_brand')

    con = {
        'title' : 'brand delete',
        'object' : brand_del,
        'brand_page' : True
    }
    return render(request, 'delete.html', con)



#---------> Product Create View here
def product_create(request):
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
    products = ProductModel.objects.filter(is_available = True).select_related('category', 'brand')
    categories = CategoryModel.objects.filter(is_active = True)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('categoryx', '').strip()
    sort = request.GET.get('sort', '').strip()

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
        products = products.order_by('-price')
    elif sort == 'high':
        products = products.order_by('price')


    con = {
        'products' : products,
        'categories' : categories,
        'query' : query,
        'selected_category' : category,
        'selected_sort' : sort
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
def product_edit(request, e_id):
    if request.user.is_customer:
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
