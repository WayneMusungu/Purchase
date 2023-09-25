from rest_framework import generics, permissions
from django.shortcuts import get_list_or_404
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders.api.serializers import OrderSerializer
from orders.services import sending


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def create(self, validated_data):
        sending(validated_data.get('phone_number'))
        return Order(**validated_data)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]


    


