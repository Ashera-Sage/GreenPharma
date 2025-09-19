
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import RegisterForm, LoginForm, ProductForm, CustomerProfileForm, SellerProfileForm
from .models import (
    Registration, CustomerProfile, SellerProfile,
    Product, Category, Cart, Order, OrderItem
)

# -------------------------------
# Home
# -------------------------------
def home(request):
    return render(request, 'greenpharma/home.html')


# -------------------------------
# Register
# -------------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.email = form.cleaned_data.get('email')
            user.save()

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
# Login
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
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
# Logout
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
    expiring_products = [p for p in products if p.expiring_soon]

    return render(request, "greenpharma/seller_dashboard.html", {
        "profile": profile,
        "products": products,
        "expiring_products": expiring_products,
    })


# -------------------------------
# Add Product
# -------------------------------
@login_required
def add_product(request):
    profile = SellerProfile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = profile
            product.save()
            messages.success(request, "✅ Product added successfully!")
            return redirect("seller_dashboard")
    else:
        form = ProductForm()
    categories = Category.objects.all()
    return render(request, "greenpharma/add_product.html", {"form": form, "categories": categories})


# -------------------------------
# Edit Product
# -------------------------------
@login_required
def edit_product(request, product_id):
    profile = SellerProfile.objects.get(user=request.user)
    product = get_object_or_404(Product, pk=product_id, seller=profile)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Product updated successfully!")
            return redirect("seller_dashboard")
    else:
        form = ProductForm(instance=product)
    return render(request, "greenpharma/edit_product.html", {"form": form, "product": product})


# -------------------------------
# Delete Product
# -------------------------------
@login_required
def delete_product(request, product_id):
    profile = SellerProfile.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id, seller=profile)
    if request.method == "POST":
        product.delete()
        messages.success(request, "❌ Product deleted successfully!")
        return redirect("seller_dashboard")
    return render(request, "greenpharma/delete_product.html", {"product": product})


# -------------------------------
# Customer Dashboard
# -------------------------------
@login_required
def customer_dashboard(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    products = Product.objects.all().select_related("seller")

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all()

    return render(request, 'greenpharma/customer_dashboard.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id or '',
    })


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "greenpharma/product_detail.html", {"product": product})


# -------------------------------
# Add to Cart
# -------------------------------
@login_required
def add_to_cart(request, product_id):
    if request.user.role != "Customer":
        messages.error(request, "Only customers can add to cart.")
        return redirect("home")

    customer = get_object_or_404(CustomerProfile, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(customer=customer, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"✅ {product.name} added to cart.")
    return redirect("view_cart")


# -------------------------------
# View Cart
# -------------------------------
@login_required
def view_cart(request):
    if request.user.role != "Customer":
        messages.error(request, "Only customers can view cart.")
        return redirect("home")

    customer = get_object_or_404(CustomerProfile, user=request.user)
    cart_items = Cart.objects.filter(customer=customer)

    total = sum(item.total_price() for item in cart_items)

    return render(request, "greenpharma/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


# -------------------------------
# Update Cart Quantity (+ / -)
# -------------------------------
@login_required
def update_cart_quantity(request, cart_id, action):
    cart_item = get_object_or_404(Cart, id=cart_id, customer__user=request.user)

    if action == "increase":
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

    return redirect("view_cart")


# -------------------------------
# Remove from Cart
# -------------------------------
@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, customer__user=request.user)
    cart_item.delete()
    messages.success(request, "❌ Item removed from cart.")
    return redirect("view_cart")


# -------------------------------
# Checkout (Dummy Payment Flow)
# -------------------------------
@login_required
def checkout(request):
    customer = get_object_or_404(CustomerProfile, user=request.user)
    cart_items = Cart.objects.filter(customer=customer)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        # ✅ Create order
        order = Order.objects.create(customer=customer, status="Pending")

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.discounted_price(),
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        return redirect("payment")

    return render(request, "greenpharma/checkout.html", {
        "customer": customer,   # ✅ Added this
        "cart_items": cart_items,
        "total": total,
    })

@login_required
def payment(request):
    return render(request, "greenpharma/payment.html")


# -------------------------------
# Customer Profile
# -------------------------------
@login_required
def customer_profile(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Profile updated successfully.")
            return redirect("customer_dashboard")
    else:
        form = CustomerProfileForm(instance=profile, user=request.user)
    return render(request, "greenpharma/customer_profile.html", {"form": form})


# -------------------------------
# Seller Profile
# -------------------------------
@login_required
def seller_profile(request):
    profile, _ = SellerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = SellerProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Profile updated successfully. Awaiting admin approval.")
            return redirect("seller_dashboard")
    else:
        form = SellerProfileForm(instance=profile, user=request.user)
    return render(request, "greenpharma/seller_profile.html", {"form": form, "profile": profile})