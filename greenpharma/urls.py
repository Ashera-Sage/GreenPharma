from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),  # ✅ add this
    path('login/', views.login_view, name='login'),          # ✅ add this
    path('logout/', views.logout_view, name='logout'),       # ✅ optional
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),  # ✅ optional
]

