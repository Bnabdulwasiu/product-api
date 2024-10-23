from rest_framework import serializers
from .models import (Product, UnitMeasurement,
                    ProductBatch, SalesRecord)

class UnitMeasurementSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnitMeasurement
        fields = ['unit_type', 'selling_price']


class AddProductQuantitySerializer(serializers.Serializer):
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)


class SellProductUnitSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    unit_type = serializers.CharField(max_length=50)  # Unit type (e.g., 'carton', 'piece', etc.)
    quantity = serializers.IntegerField(min_value=1)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class SellProductSerializer(serializers.Serializer):
    products = SellProductUnitSerializer(many=True)


class SalesRecordSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)

    class Meta:
        model = SalesRecord
        fields = ['product_name', 'unit_type', 'quantity', 'revenue', 'cost', 'profit', 'sale_date']


class RetrieveProductBatchesSerializer(serializers.ModelSerializer):
    added_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ProductBatch
        fields = ['product', 'quantity', 'cost_price', 'added_on']


class ProductSerializer(serializers.ModelSerializer):
    unit_measurements  = UnitMeasurementSerializer(many=True, required=True)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'total_quantity',
                'cost_price', 'category', 'timestamp', 'unit_measurements']
        read_only_fields = ['timestamp', 'total_quantity']

    # Create method to handle nested creation of UnitMeasurement
    def create(self, validated_data):
        unit_measurements_data = validated_data.pop('unit_measurements', [])
        product = Product.objects.create(**validated_data)
        
        # Create unit measurements if provided
        for unit_data in unit_measurements_data:
            UnitMeasurement.objects.create(product=product, **unit_data)
        
        return product