from decimal import Decimal
import json
from urllib.parse import parse_qs, urlparse
from django.test import TestCase
from django.urls import reverse
from oauth2_provider.models import get_application_model
from django.contrib.auth.models import User
from rest_framework.test import APIClient
import random
import string
import base64
import hashlib
import secrets
from Items.models import Item
from rest_framework import status

Application = get_application_model()

class ItemTestCase(TestCase):
    def setUp(self):
        # Set up test OAuth2 client credentials and other required data
        self.client_id = secrets.token_urlsafe(16)
        self.client_secret = secrets.token_urlsafe(50)
        
        # Create a test OAuth2 application
        self.application = Application.objects.create(
            name="Test Application",
            client_id=self.client_id,
            client_secret=self.client_secret,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="http://localhost:8000/o/callback",
            algorithm=Application.RS256_ALGORITHM
        )

        # Set up data for creating a superuser
        self.superuser_data = {
            'username': 'admin',
            'password': 'adminpassword',
            'email': 'admin@example.com',
        }

        # Generate code verifier and challenge for PKCE (Proof Key for Code Exchange)
        code_verifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(43, 128)))
        code_verifier = base64.urlsafe_b64encode(code_verifier.encode('utf-8'))
        self.verifier = code_verifier.decode('utf-8')

        code_challenge = hashlib.sha256(code_verifier).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').replace('=', '')
        self.challenge = code_challenge

        # Create a superuser for testing
        self.user = User.objects.create_superuser(username=self.superuser_data["username"], email=self.superuser_data['email'], password=self.superuser_data["password"])
        self.client = APIClient(raise_request_exception=True)

        # Test the OAuth2 authorization code flow
        self.client.login(username=self.superuser_data['username'], password=self.superuser_data['password'])

        authorization_url = reverse("oauth2_provider:authorize")
        response = self.client.get(
            authorization_url, {
                "response_type": "code",
                "code_challenge": self.challenge,
                "code_challenge_method": "S256",
                "client_id": self.application.client_id,
                "redirect_uri": self.application.redirect_uris.split()[0],
                "scope": "openid"
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('oauth2_provider:authorize'), {
            "response_type": "code",
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "client_id": self.application.client_id,
            "redirect_uri": self.application.redirect_uris.split()[0],
            "scope": "openid",
            'allow': True
        })
        self.assertEqual(response.status_code, 302)

        redirect_url = response.url
        parsed_url = urlparse(redirect_url)
        query_parameters = parse_qs(parsed_url.query)
        authorization_code = query_parameters.get('code', [])

        # simulate the callback url response status code
        callback_url = reverse('oauth_open_id_callback')
        response = self.client.get(callback_url, {
            'code': authorization_code[0],
            'state': secrets.token_urlsafe(50),
        })
        self.assertEqual(response.status_code, 200)

        # Request an access token using the authorization code
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code[0],
            "redirect_uri": self.application.redirect_uris.split()[0],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code_verifier": self.verifier
        }
    
        token_url = reverse("oauth2_provider:token")
        response = self.client.post(token_url, token_data)

        self.assertEqual(response.status_code, 200)

        # Check if an access token is obtained successfully and use it to make a resource request
        token_info = json.loads(response.content)
        self.access_token = token_info.get("access_token")
        self.assertIsNotNone(self.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
    
    def test_create_item_with_validation_error(self):
        # Attempt to create a item with invalid data (e.g., missing required fields)
        data = {
            # Missing 'name' field
            'size': 'L',
            'price': '29.99'
        }

        # Send a POST request to create the item
        response = self.client.post('/api/v1/items', data)
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

        # Check if the response contains error details
        self.assertTrue('name' not in response_info['results'])

    def test_read_item(self):
        # Create a test item
        item = Item.objects.create(
            name='Blueband',
            size='L',
            price='29.99'
        )

        # Send a GET request to retrieve the item details
        response = self.client.get(f'/api/v1/items/{item.id}')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the returned data matches the created item
        self.assertEqual(response_info['results']['name'], 'Blueband')
        self.assertEqual(response_info['results']['size'], 'L')
        self.assertEqual(response_info['results']['price'], '29.99')
    
    def test_list_items(self):
        # Create items in bulk    
        Item.objects.bulk_create([
            Item(name='Blueband', size='L', price='29.99'),
            Item(name='Vest', size='S', price='9.99'),
            Item(name='Shoes', size='M', price='49.99'),
            Item(name='Khai', size='XL', price='79.99'),
            Item(name='Jeans', size='XXL', price='59.99'),
        ])

        # Send a GET request to retrieve the item details
        response = self.client.get(f'/api/v1/items')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the response contains the expected number of items
        self.assertEqual(len(response_info['results']), 5)

    def test_list_item_details_with_unexpected_exception(self):
        # Create a test item
        item = Item.objects.create(
            name='Crocs',
            size='M',
            price='19.99'
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_item_id = item.id + 1000  # An invalid item ID

        # Send a GET request to retrieve the details of a item with an invalid ID
        response = self.client.get(f'/api/v1/items/{invalid_item_id}')
        response_info = json.loads(response.content)

        # Check if the request results in an error response (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

    def test_update_item(self):
        # Create a test item
        item = Item.objects.create(
            name='Jeans',
            size='S',
            price='9.99'
        )

        # Define the updated data for the item
        updated_data = {
            'name': 'Khaki',
            'size': 'XL',
            'price': '39.99',
        }

        # Send a PUT request to update the item details
        response = self.client.patch(f'/api/v1/items/{item.id}', updated_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the item details were updated in the database
        item.refresh_from_db()
        self.assertEqual(item.name, 'Khaki')
        self.assertEqual(item.size, 'XL')
        self.assertEqual(item.price, Decimal('39.99'))
    
    def test_update_item_with_validation_error(self):
        # Create a test item
        item = Item.objects.create(
            name='Jeans',
            size='S',
            price='9.99'
        )

        # Attempt to edit the item with invalid data (e.g., missing required fields)
        invalid_data = {
            'name': 'Khaki',
            'size': '',
            'price': '39.99'
        }

        # Send a PUT request to edit the item with invalid data
        response = self.client.patch(f'/api/v1/items/{item.id}', invalid_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

        # Check if the response contains error details
        self.assertTrue('first_name' not in response_info['results'])
    
    def test_update_item_with_unexpected_exception(self):
        # Create a test item
        item = Item.objects.create(
            name='Jeans',
            size='S',
            price='9.99'
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_item_id = item.id + 1000  # An invalid item ID

        # Attempt to edit the item with an invalid ID
        updated_data = {
            'name': 'Suit',
            'size': 'S',
            'price': '99.99'
        }

        # Send a PUT request to edit the item with an invalid ID
        response = self.client.patch(f'/api/v1/items/{invalid_item_id}', updated_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

    def test_delete_item(self):
        # Create a test item
        item = Item.objects.create(
            name='Sneakers',
            size='M',
            price='19.99'
        )

        # Send a DELETE request to delete the item
        response = self.client.delete(f'/api/v1/items/{item.id}')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 204 - No Content)
        self.assertEqual(response_info['status'], 204)

        # Check if the item was deleted from the database
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_delete_item_with_unexpected_exception(self):
        # Create a test item
        item = Item.objects.create(
            name='Sneakers',
            size='M',
            price='19.99'
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_item_id = item.id + 1000  # An invalid item ID

        # Send a DELETE request to delete the item with an invalid ID
        response = self.client.delete(f'/api/v1/items/{invalid_item_id}')
        response_info = json.loads(response.content)

        # Check if the request results in an error response (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)