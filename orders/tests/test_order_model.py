from django.test import TestCase
from django.utils import timezone
from customers.models import Customer
from Items.models import Item
from orders.models import Order
import uuid

class OrderModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a customer
        cls.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='0703706974'
        )

        # Create an item
        cls.item = Item.objects.create(
            name='Test Item',
            size='M',
            price='19.99'
        )

        cls.order = Order.objects.create(
            customer=cls.customer,
            item=cls.item,
            quantity=2
        )

    def test_uuid_field(self):
        self.assertIsInstance(self.order.uuid, uuid.UUID)

    def test_customer_relationship(self):
        self.assertEqual(self.order.customer, self.customer)

    def test_item_relationship(self):
        self.assertEqual(self.order.item, self.item)

    def test_quantity_field(self):
        self.assertEqual(self.order.quantity, 2)

    def test_total_property(self):
        expected_total = self.item.price * self.order.quantity
        self.assertEqual(self.order.total, expected_total)

    def test_date_created_auto_now_add(self):
        self.assertIsNotNone(self.order.date_created)
        self.assertTrue(self.order.date_created <= timezone.now())

    def test_date_modified_auto_now(self):
        initial_date_modified = self.order.date_modified
        self.assertIsNotNone(initial_date_modified)

        # Update the order
        self.order.quantity = 3
        self.order.save()

        updated_order = Order.objects.get(pk=self.order.pk)
        self.assertGreater(updated_order.date_modified, initial_date_modified)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Order._meta.verbose_name_plural), 'Orders')

    def test_string_representation(self):
        expected_string = str(self.customer)
        self.assertEqual(str(self.order), expected_string)
