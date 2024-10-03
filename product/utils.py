from django.db.models import Sum
from .models import ProductBatch

def compute_total_quantity(product):
    total_quantity = ProductBatch.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
    product.total_quantity = total_quantity
    product.save()