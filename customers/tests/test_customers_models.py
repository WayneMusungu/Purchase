from django.test import TestCase
from customers.models import Customer

class CustomerModelTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="John Doe", code="12345")
        
    def tearDown(self):
        Customer.objects.all().delete()

    def test_customer_name(self):
        self.assertEqual(self.customer.name, "John Doe")

    def test_customer_code(self):
        self.assertEqual(self.customer.code, "12345")

    def test_customer_str_method(self):
        self.assertEqual(str(self.customer), self.customer.name)