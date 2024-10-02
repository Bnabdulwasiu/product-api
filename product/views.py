from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, UnitMeasurement
from .serializers import ProductSerializer
# Create your views here.

class ProductListCreateView(generics.ListCreateAPIView):

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
