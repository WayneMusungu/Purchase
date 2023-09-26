from orders.models import Order
from rest_framework import serializers

class OrderSerializer(serializers.ModelSerializer):
    item_name = serializers.StringRelatedField(source='item.name')
    customer_first_name = serializers.StringRelatedField(source='customer.first_name')
    customer_last_name = serializers.StringRelatedField(source='customer.last_name')

    class Meta:
        model = Order
        fields = ['customer', 'customer_first_name', 'customer_last_name', 'item', 'item_name', 'quantity', 'total']