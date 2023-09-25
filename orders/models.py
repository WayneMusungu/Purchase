from django.db import models
from customers.models import Customer

# Create your models here.


class Order(models.Model):
    item = models.CharField(max_length=255)
    phone_number=models.CharField(max_length=15, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return self.item