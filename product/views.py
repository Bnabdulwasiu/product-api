from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, UnitMeasurement, ProductBatch
from .serializers import (ProductSerializer,
                        AddProductQuantitySerializer,
                        RetrieveProductBatchesSerializer)
# Create your views here.


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductRetrieveView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductBatchesRetrieveView(generics.ListAPIView):
    serializer_class = RetrieveProductBatchesSerializer
    
    def get_queryset(self):
        product_id = self.kwargs['pk']
        return ProductBatch.objects.filter(product_id=product_id)


class AddProductQuantityView(APIView):
    """
    View to handle adding a new batch for existing product stock.
    """

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = AddProductQuantitySerializer(data=request.data)

        if serializer.is_valid():
            new_quantity = serializer.validated_data['quantity']
            new_cost_price = serializer.validated_data['cost_price']

            # Create a new batch
            ProductBatch.objects.create(
                product=product,
                quantity=new_quantity,
                cost_price=new_cost_price
            )

            return Response({
                "message": f"New product batch added successfully for {product.product_name} with id {product_id}",
                "quantity": new_quantity,
                "cost_price": new_cost_price
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
