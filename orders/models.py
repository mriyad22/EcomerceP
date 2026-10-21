from django.db import models
from accounts.models import AuthUserModel
from products.models import ProductModel, ProductVariantModel
from coupons.models import CouponModel

#-------> Order Address Model
class AddressModel(models.Model):
    user = models.OneToOneField(
        AuthUserModel,
        on_delete=models.CASCADE,
        related_name='user_address'
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Bangladesh')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} --> {self.full_name} --> {self.city}"



#-----> Order Model
class OrderModel(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    user = models.ForeignKey(
        AuthUserModel, 
        on_delete=models.SET_NULL,
        related_name='user_orders',
        null=True
    )
    coupon = models.ForeignKey(CouponModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    order_number = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Bangladesh')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} --> {self.full_name} --> {self.order_number}'



#--------> Order Item Model
class OrderItemModel(models.Model):
    order = models.ForeignKey(
        OrderModel,
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.SET_NULL,
        null=True
    )

    variant = models.ForeignKey(
        ProductVariantModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} --> {self.quantity}"