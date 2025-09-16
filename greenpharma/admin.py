from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Registration,
    CustomerProfile,
    SellerProfile,
    Category,
    Product,
    Cart,
    Order,
    OrderItem,
)

# -------------------------------
# Custom Registration Admin
# -------------------------------
@admin.register(Registration)
class RegistrationAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )


# -------------------------------
# Customer Profile Admin
# -------------------------------
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address")
    search_fields = ("user__username", "phone")


# -------------------------------
# Seller Profile Admin
# -------------------------------
@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "status", "license_link")
    list_filter = ("status",)
    search_fields = ("user__username", "phone")
    readonly_fields = ("license_preview",)
    actions = ["approve_license", "reject_license"]

    def license_link(self, obj):
        if obj.license_file:
            return format_html("<a href='{}' target='_blank'>View License</a>", obj.license_file.url)
        return "No file"
    license_link.short_description = "License Document"

    def license_preview(self, obj):
        if obj.license_file:
            return format_html("<a href='{}' target='_blank'>📄 Open License File</a>", obj.license_file.url)
        return "No file uploaded"
    license_preview.short_description = "License Preview"

    def approve_license(self, request, queryset):
        queryset.update(status="Approved")
        self.message_user(request, "✅ Selected sellers have been approved.")
    approve_license.short_description = "Approve selected licenses"

    def reject_license(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "❌ Selected sellers have been rejected.")
    reject_license.short_description = "Reject selected licenses"


# -------------------------------
# Category Admin
# -------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# -------------------------------
# Product Admin
# -------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "price", "discounted_price_display", "stock", "category", "seller")
    list_filter = ("category", "seller")
    search_fields = ("name", "description")

    def thumbnail(self, obj):
        if obj.image:
            return format_html("<img src='{}' width='50' height='50' style='object-fit: cover;' />", obj.image.url)
        return "No Image"
    thumbnail.short_description = "Image"

    def discounted_price_display(self, obj):
        return f"₹{obj.discounted_price():.2f}"
    discounted_price_display.short_description = "Discounted Price"


# -------------------------------
# Cart Admin
# -------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "quantity", "total_price_display", "added_at")
    search_fields = ("customer__user__username", "product__name")
    list_filter = ("added_at",)

    def total_price_display(self, obj):
        return f"₹{obj.total_price():.2f}"
    total_price_display.short_description = "Total Price"


# -------------------------------
# OrderItem Inline
# -------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_at_purchase", "total_price_display")

    def total_price_display(self, obj):
        return f"₹{obj.total_price():.2f}"
    total_price_display.short_description = "Total"


# -------------------------------
# Order Admin
# -------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_amount_display", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__user__username",)
    inlines = [OrderItemInline]

    def total_amount_display(self, obj):
        return f"₹{obj.total_amount():.2f}"
    total_amount_display.short_description = "Total Amount"
