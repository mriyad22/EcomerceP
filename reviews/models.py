from django.db import models
from accounts.models import AuthUserModel
from products.models import ProductModel
from django.core.validators import MinValueValidator, MaxValueValidator

#------> Product review Model
class ReviewModel(models.Model):
    user = models.ForeignKey(
        AuthUserModel,
        on_delete=models.CASCADE,
        related_name='user_reviews'
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user','product'],
                name = 'one_review_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.username} -- {self.product.name} -- {self.rating}"