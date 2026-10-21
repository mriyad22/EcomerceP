from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

#-------> Coupon Model
class CouponModel(models.Model):
    code = models.CharField(max_length=50)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(90)
        ]
    )

    minimum_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}"