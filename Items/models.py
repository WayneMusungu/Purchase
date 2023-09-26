from django.db import models
import uuid

SIZES = (
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

class Item(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250, verbose_name='Name', null=False, blank=False)
    size = models.TextField(verbose_name='Size', choices=SIZES, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price', null=False, blank=False)
    date_created = models.DateTimeField(verbose_name='Date Created',auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='Date Modified',auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Items'