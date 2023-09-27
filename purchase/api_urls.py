from django.urls import path
from customers.api.views import CustomerAPIView
from Items.api.views import ItemAPIView
from orders.api.views import OrderAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class CustomerOrderAPI(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        api_urls = {
            "Title": "Customer Endpoints",
            "Create A Customer": "[POST] /v1/customers",
            "List Customers": "[GET] /v1/customers",
            "Get Customer Details": "[GET] /v1/customers/:id",
            "Update Customer Details": "[PATCH] /v1/customers/:id",
            "Delete Customer Details": "[DELETE] /v1/customers/:id",
        }, {
            "Title": "Item Endpoints",
            "Create An Item": "[POST] /v1/items",
            "List Items": "[GET] /v1/items",
            "Get Item Details": "[GET] /v1/items/:id",
            "Update Item Details": "[PATCH] /v1/items/:id",
            "Delete Item Details": "[DELETE] /v1/items/:id",
        }, {
            "Title": "Order Endpoints",
            "Create An Order": "[POST] /v1/orders",
            "List Orders": "[GET] /v1/orders",
            "Get Order Details": "[GET] /v1/orders/:id",
            "Update Order Details": "[PATCH] /v1/orders/:id",
            "Delete Order Details": "[DELETE] /v1/orders/:id",
        }

        return Response(api_urls)

urlpatterns = [
    path("", CustomerOrderAPI.as_view(), name="home"),
    path('v1/customers', CustomerAPIView.as_view(), name='list_create_customers'),
    path('v1/customers/<int:pk>', CustomerAPIView.as_view(), name="update_delete_customers"),

    path('v1/items', ItemAPIView.as_view(), name="list_create_items"),
    path('v1/items/<int:pk>', ItemAPIView.as_view(), name="update_delete_items"),

    path('v1/orders', OrderAPIView.as_view(), name="list_create_orders"),
    path('v1/orders/<int:pk>', OrderAPIView.as_view(), name="update_delete_orders"),
]