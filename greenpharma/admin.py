from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Registration, CustomerProfile, SellerProfile, Category, Product


# ✅ Custom Registration Admin
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


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address")
    search_fields = ("user__username", "phone")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "status", "license_link")  # ✅ added license link
    list_filter = ("status",)
    search_fields = ("user__username", "phone")
    readonly_fields = ("license_preview",)  # ✅ preview inside detail view
    actions = ["approve_license", "reject_license"]

    # ✅ clickable license link in list view
    def license_link(self, obj):
        if obj.license_file:
            return format_html("<a href='{}' target='_blank'>View License</a>", obj.license_file.url)
        return "No file"
    license_link.short_description = "License Document"

    # ✅ preview inside detail view
    def license_preview(self, obj):
        if obj.license_file:
            return format_html("<a href='{}' target='_blank'>📄 Open License File</a>", obj.license_file.url)
        return "No file uploaded"
    license_preview.short_description = "License Preview"

    # ✅ Approve/Reject actions
    def approve_license(self, request, queryset):
        queryset.update(status="Approved")
        self.message_user(request, "✅ Selected sellers have been approved.")
    approve_license.short_description = "Approve selected licenses"

    def reject_license(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "❌ Selected sellers have been rejected.")
    reject_license.short_description = "Reject selected licenses"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "category", "seller")
    list_filter = ("category", "seller")
    search_fields = ("name", "description")
