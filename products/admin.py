from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(BrandModel)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "discount_price", "stock", "is_available", "is_featured")


admin.site.register([
    ProductImageModel,
    ProductVariantModel
])