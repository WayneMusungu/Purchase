from rest_framework import generics, permissions
from django.shortcuts import get_list_or_404
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import re


from orders.models import Order
from orders.api.serializers import OrderSerializer
from orders.services import sending


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Access the data from the request.data dictionary
        phone_number = request.data.get('phone_number')
        
        # Validate and process the data as needed
        if not phone_number:
            return Response({'detail': 'phone_number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call your sending function
        sending(phone_number)
        # Continue with the creation of the Order
        return super().create(request, *args, **kwargs)
    
    
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]


    


