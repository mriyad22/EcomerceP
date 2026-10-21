from django.db import models
from accounts.models import AuthUserModel
from django.core.validators import MaxValueValidator, MinValueValidator

#-----> Product category model
class CategoryModel(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="media/categories/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"



#---------> Product brand model
class BrandModel(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to="media/brands/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



#--------> Product model
class ProductModel(models.Model):
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.CASCADE,
        related_name="product_category"
    )

    brand = models.ForeignKey(
        BrandModel,
        on_delete=models.SET_NULL,
        related_name="product_brand",
        null=True,
        blank=True
    )

    product_owner = models.ForeignKey(
        AuthUserModel,
        on_delete=models.CASCADE,
        related_name="user_product",
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=100, unique=True) #SKU = Stock Keeping Unit. This is a product's internal unique code.[IPH17P-256-BLK, SAM-S26U-256-BLK, DEL-IN15-I7]
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(    #It will specify what percentage of discount is being offered here.
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators = [              #It will check that the discounted price is not higher than the original price.
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
        )
    
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="media/products/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"


    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price


    @property
    def is_in_stock(self):
        return self.stock > 0



    """
    When using @property, the method does not need to be called as a function.

    General method: product.final_price()
    But in the case of a property: product.final_price

    How will you use it in the template?

        <h2>{{ product.name }}</h2>

        <p>Price: {{ product.final_price }}</p>

        {% if product.is_in_stock %}
            <button>Add to Cart</button>
        {% else %}
            <p>Out of Stock</p>
        {% endif %}
    """


#------>product image model
class ProductImageModel(models.Model):
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="product_images",
        null=True
    )

    image = models.ImageField(upload_to="media/products/gallery/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} Image"



#------> Product Variant model
class ProductVariantModel(models.Model):
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE,
        related_name="product_variants",
        null=True
    )

    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"