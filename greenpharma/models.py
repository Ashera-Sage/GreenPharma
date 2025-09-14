from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

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

    def discounted_price(self):
        if self.offer > 0:
            return self.price * (100 - self.offer) / 100
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
            return 0 <= delta.days <= 7  # Expiring in next 7 days
        return False
