from django.db import models
from accounts.models import AuthUserModel
from products.models import ProductModel

#-------> Wishlist Model
class WishlistModel(models.Model):
    user = models.OneToOneField(
        AuthUserModel,
        on_delete=models.CASCADE,
        related_name='user_wishlist'
    )

    crested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


#------> Wishlist Item model
class WishlistItemModel(models.Model):
    wishlist = models.ForeignKey(
        WishlistModel,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='wistlist_product'
    )

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product'],
                name='unique_wishlist_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name}"

