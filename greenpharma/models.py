from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from decimal import Decimal


# -------------------------------
# Custom Manager for Registration
# -------------------------------
class RegistrationManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, role="Customer", **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, role="Admin", **extra_fields)


# -------------------------------
# Custom User model
# -------------------------------
class Registration(AbstractUser):
    ROLE_CHOICES = [
        ("Customer", "Customer"),
        ("Seller", "Seller"),
        ("Admin", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Customer")

    objects = RegistrationManager()

    class Meta:
        db_table = "registration"

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------------
# Customer Profile
# -------------------------------
class CustomerProfile(models.Model):
    user = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="customer_profile")
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


# -------------------------------
# Seller Profile
# -------------------------------
class SellerProfile(models.Model):
    LICENSE_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    user = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="seller_profile")
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    license_file = models.FileField(upload_to="licenses/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=LICENSE_STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Seller: {self.user.username} ({self.status})"


# -------------------------------
# Category
# -------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# -------------------------------
# Product
# -------------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)  # Expiry date
    offer = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Discount %
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", null=True, blank=True
    )
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name="products", null=True, blank=True
    )

    def __str__(self):
        return self.name

    # ✅ Correctly indented inside class
    def discounted_price(self):
        """Return price after applying offer"""
        if self.offer > 0:
            return self.price * (Decimal(100) - self.offer) / Decimal(100)
        return self.price

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    @property
    def expiring_soon(self):
        if self.expiry_date:
            today = timezone.now().date()
            delta = self.expiry_date - today
            return 0 <= delta.days <= 7
        return False


# -------------------------------
# Cart
# -------------------------------
class Cart(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity} for {self.customer.user.username}"

    def total_price(self):
        return self.product.discounted_price() * self.quantity


# -------------------------------
# Order
# -------------------------------
class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Shipped", "Shipped"), ("Delivered", "Delivered")],
        default="Pending",
    )

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.username}"

    def total_amount(self):
        return sum(item.total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.price_at_purchase * self.quantity
