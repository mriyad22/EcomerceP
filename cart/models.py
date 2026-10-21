from django.db import models
from accounts.models import AuthUserModel
from products.models import ProductModel, ProductVariantModel

#-----> User card Model
class CartModel(models.Model):
    user = models.OneToOneField(
        AuthUserModel,
        on_delete=models.CASCADE,
        related_name='user_cart'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.cart_items.all())



#---------> Cart items model
class CartItemModel(models.Model):
    cart = models.ForeignKey(
        CartModel,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
    )

    variant = models.ForeignKey(
        ProductVariantModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product', 'variant'],
                name = 'unique_cart_product_variant'
            )
        ]

    @property
    def unit_price(self):
        if self.variant and self.variant.price is not None:
            return self.variant.price

        return self.product.final_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


    # @property
    # def total_price(self):
    #     price = (
    #         self.variant.price if self.variant and self.variant.price else self.product.final_price
    #     )
    #     return price * self.quantity