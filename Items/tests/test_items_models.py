from django.test import TestCase
from django.utils import timezone
from Items.models import Item, SIZES
import uuid

class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.item = Item.objects.create(
            name='Test Item',
            size='M',
            price='19.99'
        )

    def test_uuid_field(self):
        self.assertIsInstance(self.item.uuid, uuid.UUID)

    def test_name_max_length(self):
        max_length = self.item._meta.get_field('name').max_length
        self.assertLessEqual(len(self.item.name), max_length)

    def test_size_choices(self):
        size_field = self.item._meta.get_field('size')
        self.assertTrue(all(choice[0] in dict(SIZES) for choice in size_field.choices))

    def test_price_decimal_places(self):
        decimal_places = self.item._meta.get_field('price').decimal_places
        self.assertEqual(decimal_places, 2)

    def test_date_created_auto_now_add(self):
        self.assertIsNotNone(self.item.date_created)
        self.assertTrue(self.item.date_created <= timezone.now())

    def test_date_modified_auto_now(self):
        initial_date_modified = self.item.date_modified
        self.assertIsNotNone(initial_date_modified)

        # Update the item
        self.item.name = 'Updated Item'
        self.item.save()

        updated_item = Item.objects.get(pk=self.item.pk)
        self.assertGreater(updated_item.date_modified, initial_date_modified)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Item._meta.verbose_name_plural), 'Items')

    def test_string_representation(self):
        expected_string = self.item.name
        self.assertEqual(str(self.item), expected_string)
