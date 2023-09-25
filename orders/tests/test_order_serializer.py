import json
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from orders.models import Order
from customers.models import Customer
from django.urls import reverse
from orders.api.serializers import OrderSerializer

class OrderSerializerTestCase(TestCase):
    def setUp(self):
        self.customer_data = {'name': 'John Doe', 'code': '12345'}
        self.customer = Customer.objects.create(**self.customer_data)
        self.order_data = {
            'item': 'Strawberries',
            'phone_number': '0789745623',
            'amount': '10.99',
            'customer': self.customer.pk,
        }

    def test_valid_serializer(self):
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid_serializer_missing_item(self):
        invalid_data = self.order_data.copy()
        del invalid_data['item']
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
    def test_invalid_serializer_missing_amount(self):
        invalid_data = self.order_data.copy()
        del invalid_data['amount']
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
    def test_create_order(self):
        response = self.client.post(reverse('order-list-create'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.last().item, 'Strawberries')
        
    def test_update_order(self):
        customer = Customer.objects.create(name='John Doe', code='12345')        
        order = Order.objects.create(item='Chair', phone_number='0795678490', amount='50.00', customer=customer)
        
        updated_customer_data = {
            'name': 'Updated Customer',
            'code': '54321',
        }
        updated_customer = Customer.objects.create(**updated_customer_data)
        
        updated_data = {
            'item': 'Table',
            'phone_number': '0795678490',
            'amount': '75.00',
            'customer': updated_customer.pk,
        }
        
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = self.client.patch(url, json.dumps(updated_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        order.refresh_from_db()
        self.assertEqual(order.item, 'Table')
        
    def test_delete_order(self):
        customer = Customer.objects.create(name='John Doe', code='12345')
        order = Order.objects.create(item='Chair', phone_number='0795678490', amount='50.00', customer=customer)
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())
    