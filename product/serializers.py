from rest_framework import serializers
from .models import Product, UnitMeasurement

class UnitMeasurementSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnitMeasurement
        fields = ['unit_type', 'selling_price']

class AddProductQuantitySerializer(serializers.Serializer):
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField(min_value=1)
        
class ProductSerializer(serializers.ModelSerializer):
    unit_measurements  = UnitMeasurementSerializer(many=True, required=True)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'quantity', 'cost_price', 'category', 'timestamp', 'unit_measurements']
        read_only_fields = ['timestamp']

    # Create method to handle nested creation of UnitMeasurement
    def create(self, validated_data):
        unit_measurements_data = validated_data.pop('unit_measurements', [])
        product = Product.objects.create(**validated_data)
        
        # Create unit measurements if provided
        for unit_data in unit_measurements_data:
            UnitMeasurement.objects.create(product=product, **unit_data)
        
        return product