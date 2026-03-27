from django.urls import path
from . import views

urlpatterns = [

    # ================= AUTH ================= #
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ================= DASHBOARD ================= #
    path('', views.dashboard, name='dashboard'),

    # ================= PRODUCTS ================= #
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/update/<int:pk>/', views.update_product, name='update_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),

    # ================= SUPPLIERS ================= #
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/update/<int:pk>/', views.update_supplier, name='update_supplier'),
    path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete_supplier'),

    # ================= REPORTS ================= #
    path('reports/', views.reports, name='reports'),

    # ================= INVOICE ================= #
    path('invoice/<int:pk>/', views.generate_invoice, name='generate_invoice'),

    # 🔥 ADD THIS LINE HERE
    path('transaction/add/', views.add_transaction, name='add_transaction'),
]