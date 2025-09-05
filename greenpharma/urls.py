from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),  # Added customer dashboard
    path("dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("seller/add-product/", views.add_product, name="add_product"),
]
