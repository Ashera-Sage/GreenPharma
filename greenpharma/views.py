from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import RegisterForm, LoginForm, ProductForm, CustomerProfileForm, SellerProfileForm
from .models import Registration, CustomerProfile, SellerProfile, Product, Category


# -------------------------------
# Home Page
# -------------------------------
def home(request):
    return render(request, 'greenpharma/home.html')


# -------------------------------
# Register View
# -------------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.email = form.cleaned_data.get('email')
            user.save()

            # create role-based profile
            if role == "Customer":
                CustomerProfile.objects.create(user=user)
            elif role == "Seller":
                SellerProfile.objects.create(user=user)

            messages.success(request, "Registration successful. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'greenpharma/register.html', {'form': form})


# -------------------------------
# Login View
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                if user.role == "Customer":
                    return redirect("customer_dashboard")
                elif user.role == "Seller":
                    return redirect("seller_dashboard")
                elif user.role == "Admin":
                    return redirect("/admin/")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'greenpharma/login.html', {'form': form})


# -------------------------------
# Logout View
# -------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# -------------------------------
# Seller Dashboard
# -------------------------------
@login_required
def seller_dashboard(request):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Please complete your seller profile first.")
        return redirect("seller_profile")

    products = Product.objects.filter(seller=profile)
    return render(request, "greenpharma/seller_dashboard.html", {
        "profile": profile,
        "products": products,
    })


# -------------------------------
# Add Product
# -------------------------------
@login_required
def add_product(request):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Please complete your seller profile first.")
        return redirect("seller_profile")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = profile
            product.save()
            messages.success(request, "✅ Product added successfully!")
            return redirect("seller_dashboard")
        else:
            messages.error(request, "⚠️ Error adding product. Please check the form.")
    else:
        form = ProductForm()

    return render(request, "greenpharma/add_product.html", {"form": form})


# -------------------------------
# Edit Product
# -------------------------------
@login_required
def edit_product(request, product_id):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Please complete your seller profile first.")
        return redirect("seller_profile")

    product = get_object_or_404(Product, pk=product_id, seller=profile)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Product updated successfully!")
            return redirect("seller_dashboard")
        else:
            messages.error(request, "⚠️ Error updating product. Please check the form.")
    else:
        form = ProductForm(instance=product)

    return render(request, "greenpharma/edit_product.html", {
        "form": form,
        "product": product
    })


# -------------------------------
# Delete Product
# -------------------------------
@login_required
def delete_product(request, product_id):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        messages.error(request, "Please complete your seller profile first.")
        return redirect("seller_profile")

    product = get_object_or_404(Product, id=product_id, seller=profile)

    if request.method == "POST":
        product.delete()
        messages.success(request, "❌ Product deleted successfully!")
        return redirect("seller_dashboard")

    return render(request, "greenpharma/delete_product.html", {"product": product})


# -------------------------------
# Customer Dashboard
# -------------------------------
def customer_dashboard(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all().select_related("seller")

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    return render(request, 'greenpharma/customer_dashboard.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
    })


# -------------------------------
# Customer Profile
# -------------------------------
@login_required
def profile_view(request):
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Profile updated successfully.")
            return redirect("customer_dashboard")
    else:
        form = CustomerProfileForm(instance=profile, user=request.user)

    return render(request, "greenpharma/profile.html", {"form": form})


# -------------------------------
# Seller Profile (FIXED)
# -------------------------------
@login_required
def seller_profile(request):
    try:
        profile = SellerProfile.objects.get(user=request.user)
    except SellerProfile.DoesNotExist:
        profile = SellerProfile(user=request.user)

    if request.method == "POST":
        form = SellerProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Profile updated successfully. Awaiting admin approval.")
            return redirect("seller_dashboard")
        else:
            # Display form errors for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SellerProfileForm(instance=profile, user=request.user)

    return render(request, "greenpharma/seller_profile.html", {
        "form": form,
        "profile": profile,
    })
