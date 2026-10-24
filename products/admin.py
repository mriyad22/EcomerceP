from django.contrib import admin
from .models import *

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(BrandModel)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}   #---> Generate a slug from the product name


class ProductImageInline(admin.TabularInline):  #---> 'TabularInline' Displays the related model in a table format
    model = ProductImageModel   #---> Determines which model's information will be displayed inline.
    extra = 1   #---> An additional empty form is displayed for adding a new image.


class ProductVariantInline(admin.TabularInline):
    model = ProductVariantModel
    extra = 1   #---> An additional empty form is displayed for adding a new variant.


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "discount_price", "stock", "is_available", "is_featured")
    list_filter = ('category', 'brand', 'is_available', 'is_featured')
    search_fields = ('name', 'sku') #---> You can search for products by name or SKU using the search box in the Admin Panel.
    prepopulated_fields = { 'slug':('name',)}
    inlines = [ProductImageInline, ProductVariantInline]    #---> This line adds ProductImageInline and ProductVariantInline to ProductAdmin.
    


