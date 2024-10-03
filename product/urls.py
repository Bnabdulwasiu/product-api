from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveView.as_view(), name='single-product'),
    path('products/<int:product_id>/add-quantity/', views.AddProductQuantityView.as_view(), name='add-product-quantity'),
    path('products/<int:pk>/product-batches/', views.ProductBatchesRetrieveView.as_view(), name='add-product-quantity')
]