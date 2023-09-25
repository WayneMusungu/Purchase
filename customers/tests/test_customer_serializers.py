import json
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from customers.models import Customer
from django.urls import reverse
from customers.api.serializers import CustomerSerializer

class CustomerCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.customer_data = {'name': 'John Doe', 'code': '12345'}
        self.customer = Customer.objects.create(**self.customer_data)
        self.url = reverse('customer-list-create')
        self.response = self.client.get(self.url)

    def test_valid_serializer(self):
        serializer = CustomerSerializer(data=self.customer_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_serializer_missing_name(self):
        invalid_data = self.customer_data.copy()
        del invalid_data['name']
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_serializer_missing_code(self):
        invalid_data = self.customer_data.copy()
        del invalid_data['code']
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
    def test_get_customers(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.response.data), 1)
        self.assertEqual(self.response.data[0]['name'], 'John Doe')
        
    def test_create_customer(self):
        new_customer_data = {
            'name': 'Eva Smith',
            'code': '54321',
        }
        response = self.client.post(self.url, new_customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Customer.objects.last().name, 'Eva Smith')
        
    def test_update_customer(self):
        updated_data = {
            'name': 'Updated Name',
            'code': '54321',
        }
        url = reverse('customer-list-update', kwargs={'pk': self.customer.pk})
        response = self.client.patch(url, json.dumps(updated_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Name')
        
    def test_delete_customer(self):
        url = reverse('customer-list-update', kwargs={'pk': self.customer.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())
            
        
