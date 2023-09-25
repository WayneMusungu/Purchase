from django.test import TestCase
from django.utils import timezone
from orders.models import Order
from customers.models import Customer


class OrderModelTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="John Doe", code="12345")
        self.order = Order.objects.create(
            item="Laptop",
            phone_number="0798456789",
            amount=99.99,
            time=timezone.now(),
            customer=self.customer,
        )
        
    def tearDown(self):
        Customer.objects.all().delete()
        Order.objects.all().delete()

    def test_order_item(self):
        self.assertEqual(str(self.order), "Laptop")

    def test_order_customer_relationship(self):
        self.assertEqual(self.order.customer, self.customer)

    def test_order_phone_number(self):
        self.assertEqual(self.order.phone_number, "0798456789")

    def test_order_amount(self):
        self.assertEqual(float(self.order.amount), 99.99)

    def test_order_time(self):
        self.assertTrue(timezone.now() >= self.order.time)

    def test_order_str_method(self):
        self.assertEqual(str(self.order), self.order.item)