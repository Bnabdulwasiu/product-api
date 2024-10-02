from django.db import models

PRODUCT_CATEGORY = [
    ("drugs", "Drugs"),
    ("cosmetics", "Cosmetics"),
    ("food", "Food"),
    ("clothing", "Flothing")
]

UNIT_CHOICES = [
    ("piece", "Piece"),
    ("kg", "KG"),
    ("carton", "Carton"),
    ("bag", "Bag")
]

# Create your models here.
class Product(models.Model):

    product_name = models.CharField(max_length=250)
    # Total stock quantity
    total_quantity = models.IntegerField()
    cost_price  = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=15, choices=PRODUCT_CATEGORY)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.product_name} has been added to the product catalogue"

class UnitMeasurement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="unit_measurements")
    unit_type = models.CharField(max_length=50, choices=UNIT_CHOICES)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.unit_type} of {self.product.product_name} at NGN{self.selling_price}"