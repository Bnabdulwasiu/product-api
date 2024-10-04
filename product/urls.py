from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Product API",
        default_version="v1",
        description="API for managing products, sales, and product batches.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


urlpatterns = [
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveView.as_view(), name='single-product'),
    path('products/<int:product_id>/add-quantity/', views.AddProductQuantityView.as_view(), name='add-product-quantity'),
    path('products/<int:pk>/product-batches/', views.ProductBatchesRetrieveView.as_view(), name='add-product-quantity'),
    path('products/sell/', views.SellProductView.as_view(), name='sell-product'),
    path("sales-history/", views.SalesHistoryView.as_view(), name='sales-history'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]