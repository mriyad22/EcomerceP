from django.db import models


class TrendStuffModel(models.Model):
    image_url = models.URLField(max_length=500, null=True, unique=True)
    heading = models.CharField(max_length=255)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.heading}'
