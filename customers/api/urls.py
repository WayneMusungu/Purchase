from django.urls import path
from customers.api.views import CustomerListCreateView, CustomerDetailView

urlpatterns = [
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
]