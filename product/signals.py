from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductBatch
from .utils import compute_total_quantity

@receiver(post_save, sender=ProductBatch)
@receiver(post_delete, sender=ProductBatch)
def update_total_quantity(sender, instance, **kwargs):
    product = instance.product
    compute_total_quantity(product)
