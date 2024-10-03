from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, ProductBatch
from decimal import Decimal
from .serializers import (ProductSerializer,
                        AddProductQuantitySerializer,
                        RetrieveProductBatchesSerializer,
                        SellProductSerializer)
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


class SellProductView(APIView):

     def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)

        serializer = SellProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        selling_price = Decimal(request.data.get('selling_price'))
        quantity_to_sell = int(request.data.get('quantity'))

        # FIFO: Get batches in order of when they were added (oldest first)
        batches = ProductBatch.objects.filter(product=product).order_by('added_on')

        total_cost = Decimal(0)
        total_sold = 0

        for batch in batches:
            if quantity_to_sell == 0:
                break

            elif batch.quantity <= quantity_to_sell:
                # If the current batch can be fully sold
                total_cost += batch.quantity * batch.cost_price
                quantity_to_sell -= batch.quantity
                total_sold += batch.quantity

                # Delete the batch since it has been sold completely
                batch.delete()
            else:
                # If only part of the batch is sold
                total_cost += quantity_to_sell * batch.cost_price
                batch.quantity -= quantity_to_sell
                batch.save()

                total_sold += quantity_to_sell
                quantity_to_sell = 0

        if total_sold == 0:
            return Response({"message": "No products available to sell"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total profit
        total_revenue = total_sold * selling_price
        profit = total_revenue - total_cost

        return Response({
            "message": f"{total_sold} units of {product.product_name} sold.",
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "profit": profit
        }, status=status.HTTP_200_OK)