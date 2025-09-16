from django.urls import path
from . import views

urlpatterns = [
    # General
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    

    # Seller
    path("seller-dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/profile/", views.seller_profile, name="seller_profile"),
    path("seller/add-product/", views.add_product, name="add_product"),
    path("seller/edit-product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("seller/delete-product/<int:product_id>/", views.delete_product, name="delete_product"),


    # Customer
    path("customer-dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("customer_profile/", views.customer_profile, name="customer_profile"),
    path("customer/product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/checkout/", views.checkout, name="checkout"),
]

