from django.db import models
from django.conf import settings
from orders.models import OrderModel

#------> Payment Model 
class PaymentModel(models.Model):
    PAYMENT_METHOD = [
        ('COD', 'Cash on Delivery'),
        ('CARD', 'Card'),
        ('MOBILE_BANKING', 'Mobile Banking')
    ]

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    order = models.OneToOneField(
        OrderModel,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} -- {self.status}"