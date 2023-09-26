import json
import os
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
from orders.models import Order
from customers.models import Customer
from Items.models import Item
from dotenv import load_dotenv
import phonenumbers
import africastalking as at
from rest_framework import status
from decouple import config
from purchase.settings import API_KEY, USERNAME, SENDER


# Initialize the Africas Talking client with the required credentials
at.initialize(USERNAME, API_KEY)

# Initialize a service, in this case, SMS
sms = at.SMS

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

    # def test_create_order(self):
    #     # Create test customer and item
    #     customer = Customer.objects.create(
    #         first_name='John',
    #         last_name='Snow',
    #         phone_number='0798567357'
    #     )
    #     item = Item.objects.create(
    #         name='Sneakers',
    #         size='M',
    #         price='19.99'
    #     )

    #     # Define the data for the new order
    #     data = {
    #         'customer': customer.id,
    #         'item': item.id,
    #         'quantity': 3,
    #     }

    #     # Send a POST request to create a new order
    #     response = self.client.post('/api/v1/orders', data)
    #     response_info = json.loads(response.content)

    #     # Check if the request was successful (HTTP status code 201 - Created)
    #     self.assertEqual(response_info['status'], 201)

    #     # Check if the order was created in the database
    #     self.assertTrue(Order.objects.filter(customer=customer, item=item, quantity=3).exists())

    #     # Parse and validate the phone number using the phonenumbers library
    #     parsed_phone_number = phonenumbers.parse(customer.phone_number, 'KE')
    #     validated_phone_number = phonenumbers.format_number(parsed_phone_number, phonenumbers.PhoneNumberFormat.E164)

    #     # Compose the SMS message with order details
    #     message = f"Hello {customer.first_name} {customer.last_name}, this is to inform you that your order of {data['quantity']} {item}(s), for a total of Ksh. {response_info['results']['total']} is ready for pickup. Thank you for your service."
        
    #     # Send the customized message to the validated phone number
    #     response = sms.send(message, [validated_phone_number], SENDER)
    #     print(response)

    #     # Check if the sms response was successful (HTTP status code 101 - Success)
    #     self.assertEqual(response['SMSMessageData']['Recipients'][0]['statusCode'], 101)

    def test_create_item_with_validation_error(self):
        # Attempt to create a item with invalid data (e.g., missing required fields)
        item = Item.objects.create(
            name='Sneakers',
            size='M',
            price='19.99'
        )

        # Define the data for the new order
        data = {
            # Missing 'customer' field
            'item': item.id,
            'quantity': 3,
        }

        # Send a POST request to create the item
        response = self.client.post('/api/v1/orders', data)
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

        # Check if the response contains error details
        self.assertTrue('name' not in response_info['results'])

    def test_read_order(self):
        # Create a test order
        customer = Customer.objects.create(
            first_name='Jane',
            last_name='Flin',
            phone_number='0755678923'
        )
        item = Item.objects.create(
            name='Sweater',
            size='L',
            price='29.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=2,
        )

        # Send a GET request to retrieve the order details
        response = self.client.get(f'/api/v1/orders/{order.id}')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the returned data matches the created order
        self.assertEqual(response_info['results']['customer'], customer.id)
        self.assertEqual(response_info['results']['item'], item.id)
        self.assertEqual(response_info['results']['quantity'], 2)

    def test_list_orders(self):
        # Create customers in bulk
        customer = Customer.objects.create(
            first_name='Michael',
            last_name='Fling',
            phone_number='0755678923'
        )
        item = Item.objects.create(
            name='Sweater',
            size='L',
            price='29.99'
        )

        # Create orders in bulk
        Order.objects.bulk_create([
            Order(customer=customer, item=item, quantity=1),
            Order(customer=customer, item=item, quantity=2),
            Order(customer=customer, item=item, quantity=3),
            Order(customer=customer, item=item, quantity=4),
            Order(customer=customer, item=item, quantity=5),
        ])

        # Send a GET request to retrieve the customer details
        response = self.client.get(f'/api/v1/orders')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the response contains the expected number of orders
        self.assertEqual(len(response_info['results']), 5)

    def test_list_item_details_with_unexpected_exception(self):
        # Create a test item
        customer = Customer.objects.create(
            first_name='Jane',
            last_name='Flin',
            phone_number='0755678923'
        )
        item = Item.objects.create(
            name='Sweater',
            size='L',
            price='29.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=2,
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_order_id = order.id + 1000  # An invalid item ID

        # Send a GET request to retrieve the details of a item with an invalid ID
        response = self.client.get(f'/api/v1/orders/{invalid_order_id}')
        response_info = json.loads(response.content)

        # Check if the request results in an error response (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

    def test_update_order(self):
        # Create a test order
        customer = Customer.objects.create(
            first_name='Alice',
            last_name='Blue',
            phone_number='0788946523'
        )
        item = Item.objects.create(
            name='Gloves',
            size='S',
            price='9.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=1,
        )

        # Define the updated data for the order
        updated_data = {
            'customer': customer.id,
            'item': item.id,
            'quantity': 5,
        }

        # Send a PUT request to update the order details
        response = self.client.patch(f'/api/v1/orders/{order.id}', updated_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 200 - OK)
        self.assertEqual(response_info['status'], 200)

        # Check if the order details were updated in the database
        order.refresh_from_db()
        self.assertEqual(order.quantity, 5)

    def test_update_item_with_validation_error(self):
        # Create a test item
        customer = Customer.objects.create(
            first_name='Alice',
            last_name='Blue',
            phone_number='0788946523'
        )
        item = Item.objects.create(
            name='Gloves',
            size='S',
            price='9.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=1,
        )

        # Attempt to edit the item with invalid data (e.g., missing required fields)
        invalid_data = {
            'customer': customer.id,
            'item': item.id,
            'quantity': '',
        }

        # Send a PUT request to edit the item with invalid data
        response = self.client.patch(f'/api/v1/orders/{order.id}', invalid_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

        # Check if the response contains error details
        self.assertTrue('first_name' not in response_info['results'])
    
    def test_update_item_with_unexpected_exception(self):
        # Create a test item
        customer = Customer.objects.create(
            first_name='Alice',
            last_name='Blue',
            phone_number='0788946523'
        )
        item = Item.objects.create(
            name='Gloves',
            size='S',
            price='9.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=1,
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_order_id = order.id + 1000  # An invalid item ID

        # Attempt to edit the item with an invalid ID
        updated_data = {
            'name': 'Suit',
            'size': 'S',
            'price': '99.99'
        }

        # Send a PUT request to edit the item with an invalid ID
        response = self.client.patch(f'/api/v1/orders/{invalid_order_id}', updated_data, format='json')
        response_info = json.loads(response.content)

        # Check if the request results in a validation error (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)

    def test_delete_order(self):
        # Create a test order
        customer = Customer.objects.create(
            first_name='Bob',
            last_name='White',
            phone_number='0784611250'
        )
        item = Item.objects.create(
            name='Sneakers',
            size='M',
            price='19.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=3,
        )

        # Send a DELETE request to delete the order
        response = self.client.delete(f'/api/v1/orders/{order.id}')
        response_info = json.loads(response.content)

        # Check if the request was successful (HTTP status code 204 - No Content)
        self.assertEqual(response_info['status'], 204)

        # Check if the order was deleted from the database
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_delete_item_with_unexpected_exception(self):
        # Create a test item
        customer = Customer.objects.create(
            first_name='Bob',
            last_name='White',
            phone_number='0784611250'
        )
        item = Item.objects.create(
            name='Sneakers',
            size='M',
            price='19.99'
        )
        order = Order.objects.create(
            customer=customer,
            item=item,
            quantity=3,
        )

        # Simulate an unexpected exception by manipulating the item ID
        invalid_order_id = order.id + 1000  # An invalid item ID

        # Send a DELETE request to delete the item with an invalid ID
        response = self.client.delete(f'/api/v1/orders/{invalid_order_id}')
        response_info = json.loads(response.content)

        # Check if the request results in an error response (HTTP status code 400 - Bad Request)
        self.assertEqual(response_info['status'], status.HTTP_400_BAD_REQUEST)