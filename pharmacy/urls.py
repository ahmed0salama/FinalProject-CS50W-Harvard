from django.urls import path
from . import views

urlpatterns = [
    # Main 'catalog'
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ERP
    path('erp/', views.erp_dashboard, name='erp_dashboard'),
    path('erp/inventory/', views.erp_inventory_list, name='erp_inventory'),
    path('erp/products/add/', views.erp_product_create, name='erp_product_create'),
    path('erp/products/<int:product_id>/edit/', views.erp_product_edit, name='erp_product_edit'),
    path('erp/products/<int:product_id>/stock-adjust/', views.erp_stock_adjust, name='erp_stock_adjust'),
    path('erp/pos/', views.erp_pos_view, name='erp_pos'),
    path('api/pos/checkout/', views.api_pos_checkout, name='api_pos_checkout'),
    path('erp/vendors/', views.erp_vendor_list, name='erp_vendors'),
    path('erp/purchases/', views.erp_purchase_order_list, name='erp_purchases'),
    path('erp/purchases/new/', views.erp_purchase_order_create, name='erp_purchase_create'),

    # APIs
    path('api/search/', views.api_search_products, name='api_search_products'),
    path('api/alternatives/<int:product_id>/', views.api_get_alternatives, name='api_get_alternatives'),
    path('api/cart/add/', views.api_cart_reserve, name='api_cart_reserve'),
    path('api/cart/', views.api_get_cart, name='api_get_cart'),
]