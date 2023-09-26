from django.test import TestCase
from django.utils import timezone
from customers.models import Customer
import uuid

class CustomerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            phone_number='1234567890'
        )

    def test_uuid_field(self):
        self.assertIsInstance(self.customer.uuid, uuid.UUID)

    def test_first_name_max_length(self):
        max_length = self.customer._meta.get_field('first_name').max_length
        self.assertLessEqual(len(self.customer.first_name), max_length)

    def test_last_name_max_length(self):
        max_length = self.customer._meta.get_field('last_name').max_length
        self.assertLessEqual(len(self.customer.last_name), max_length)

    def test_phone_number_max_length(self):
        max_length = self.customer._meta.get_field('phone_number').max_length
        self.assertLessEqual(len(self.customer.phone_number), max_length)

    def test_first_name_blank(self):
        field = self.customer._meta.get_field('first_name')
        self.assertFalse(field.blank)

    def test_last_name_blank(self):
        field = self.customer._meta.get_field('last_name')
        self.assertFalse(field.blank)

    def test_phone_number_blank(self):
        field = self.customer._meta.get_field('phone_number')
        self.assertFalse(field.blank)

    def test_date_created_auto_now_add(self):
        self.assertIsNotNone(self.customer.date_created)
        self.assertTrue(self.customer.date_created <= timezone.now())

    def test_date_modified_auto_now(self):
        initial_date_modified = self.customer.date_modified
        self.assertIsNotNone(initial_date_modified)

        # Update the customer
        self.customer.first_name = 'Jane'
        self.customer.save()

        updated_customer = Customer.objects.get(pk=self.customer.pk)
        self.assertGreater(updated_customer.date_modified, initial_date_modified)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Customer._meta.verbose_name_plural), 'Customers')

    def test_string_representation(self):
        expected_string = f'{self.customer.first_name} {self.customer.last_name}'
        self.assertEqual(str(self.customer), expected_string)
