from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Product, ProductBatch, SalesRecord
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from .serializers import (ProductSerializer,
                        AddProductQuantitySerializer,
                        RetrieveProductBatchesSerializer,
                        SellProductSerializer, SalesRecordSerializer)
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
    

class SalesHistoryView(generics.ListAPIView):

    serializer_class = SalesRecordSerializer

    def get_queryset(self):
        return SalesRecord.objects.all().order_by('-sale_date')


class AddProductQuantityView(APIView):
    """
    View to handle adding a new batch for existing product stock.
    """
    @swagger_auto_schema(
        request_body=AddProductQuantitySerializer,
        responses={201: 'Created', 400: 'Bad Request'},
        operation_description="Add quantity to an existing product. Requires `cost_price` and `quantity`."
    )

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
    """
    View to handle selling multiple products in one transaction.
    """

    @swagger_auto_schema(
        request_body=SellProductSerializer,
        responses={200: 'Success', 400: 'Bad Request'},
        operation_description="Sell multiple products in one transaction. Requires a list of `product_id`, `unit_type`, `quantity`, and `selling_price`."
    )
    def post(self, request):
        serializer = SellProductSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        total_transaction_profit = Decimal(0)
        total_revenue = Decimal(0)
        total_cost = Decimal(0)
        details = []

        with transaction.atomic():
            for product_sale_data in serializer.validated_data['products']:
                product_id = product_sale_data['product_id']
                unit_type = product_sale_data['unit_type']
                quantity_to_sell = product_sale_data['quantity']
                selling_price = product_sale_data['selling_price']

                product = get_object_or_404(Product, pk=product_id)

                available_unit_types = product.unit_measurements.values_list('unit_type', flat=True)
                print(f"Available unit types for product {product.product_name}: {available_unit_types}")

                # Validate the unit measurement for the product
                unit_measurement = product.unit_measurements.filter(unit_type=unit_type,).first()
                if not unit_measurement:
                    return Response({"error": f"Unit type '{unit_type}' is not valid for product {product.product_name}."}, 
                                    status=status.HTTP_400_BAD_REQUEST)

                # FIFO: Get batches in order of when they were added (oldest first)
                batches = ProductBatch.objects.filter(product=product).order_by('added_on')

                product_total_cost = Decimal(0)
                total_sold = 0

                for batch in batches:
                    if quantity_to_sell == 0:
                        break

                    if batch.quantity <= quantity_to_sell:
                        # If the current batch can be fully sold
                        product_total_cost += batch.quantity * batch.cost_price
                        quantity_to_sell -= batch.quantity
                        total_sold += batch.quantity

                        # Delete the batch since it has been sold completely
                        batch.delete()
                    else:
                        # If only part of the batch is sold
                        product_total_cost += quantity_to_sell * batch.cost_price
                        batch.quantity -= quantity_to_sell
                        batch.save()

                        total_sold += quantity_to_sell
                        quantity_to_sell = 0

                if total_sold == 0:
                    return Response({"message": f"No products available to sell for {product.product_name}"},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Calculate profit for this product sale
                product_revenue = total_sold * selling_price
                product_profit = product_revenue - product_total_cost

                SalesRecord.objects.create(
                    product=product,
                    unit_type=unit_type,
                    quantity=total_sold,
                    revenue=product_revenue,
                    cost=product_total_cost,
                    profit=product_profit,
                )

                total_transaction_profit += product_profit
                total_revenue += product_revenue
                total_cost += product_total_cost

                details.append({
                    "product": product.product_name,
                    "units_sold": total_sold,
                    "unit_type": unit_type,
                    "total_revenue": product_revenue,
                    "total_cost": product_total_cost,
                    "profit": product_profit
                })

            return Response({
                "message": "Products sold successfully.",
                "transaction_summary": {
                    "total_revenue": total_revenue,
                    "total_cost": total_cost,
                    "total_profit": total_transaction_profit
                },
                "details": details
            }, status=status.HTTP_200_OK)


# class SellProductView(APIView):

#      def post(self, request, product_id):
#         product = get_object_or_404(Product, pk=product_id)

#         serializer = SellProductSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         selling_price = Decimal(request.data.get('selling_price'))
#         quantity_to_sell = int(request.data.get('quantity'))

#         # FIFO: Get batches in order of when they were added (oldest first)
#         batches = ProductBatch.objects.filter(product=product).order_by('added_on')

#         total_cost = Decimal(0)
#         total_sold = 0

#         for batch in batches:
#             if quantity_to_sell == 0:
#                 break

#             elif batch.quantity <= quantity_to_sell:
#                 # If the current batch can be fully sold
#                 total_cost += batch.quantity * batch.cost_price
#                 quantity_to_sell -= batch.quantity
#                 total_sold += batch.quantity

#                 # Delete the batch since it has been sold completely
#                 batch.delete()
#             else:
#                 # If only part of the batch is sold
#                 total_cost += quantity_to_sell * batch.cost_price
#                 batch.quantity -= quantity_to_sell
#                 batch.save()

#                 total_sold += quantity_to_sell
#                 quantity_to_sell = 0

#         if total_sold == 0:
#             return Response({"message": "No products available to sell"}, status=status.HTTP_400_BAD_REQUEST)

#         # Calculate total profit
#         total_revenue = total_sold * selling_price
#         profit = total_revenue - total_cost

#         return Response({
#             "message": f"{total_sold} units of {product.product_name} sold.",
#             "total_revenue": total_revenue,
#             "total_cost": total_cost,
#             "profit": profit
#         }, status=status.HTTP_200_OK)