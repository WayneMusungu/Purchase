from django.db import models
import uuid

class Customer(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=250, verbose_name='First Name', null=False, blank=False)
    last_name = models.CharField(max_length=250, verbose_name='Last Name', null=False, blank=False)
    phone_number = models.CharField(max_length=250, verbose_name='Phone Number', null=False, blank=False)
    date_created = models.DateTimeField(verbose_name='Date Created',auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='Date Modified',auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        verbose_name_plural = 'Customers'