from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm, RegisterForm, LoginForm
from .models import Profile, Product, Category

# Home Page
def home(request):
    return render(request, 'greenpharma/home.html')

# Register View
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')

            # Save extra fields into User model
            user.email = form.cleaned_data.get('email')
            user.save()

            # ✅ Create linked Profile
            Profile.objects.create(
                user=user,
                role=role
            )

            messages.success(request, "Registration successful. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'greenpharma/register.html', {'form': form})


# Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role').lower()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    profile = user.profile
                    if profile.role != role:
                        messages.error(request, f"You are not registered as {role}.")
                    else:
                        login(request, user)
                        if role == "seller":   # ✅ lowercase seller
                            return redirect('seller_dashboard')
                        return redirect('customer_dashboard')
                except Profile.DoesNotExist:
                    messages.error(request, "Profile not found. Please register again.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'greenpharma/login.html', {'form': form})


# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# Seller Dashboard
def seller_dashboard(request):
    return render(request, 'greenpharma/seller_dashboard.html')

# Customer Dashboard
def customer_dashboard(request):
    query = request.GET.get('q')  # search keyword
    category_id = request.GET.get('category')  # selected category

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'greenpharma/customer_dashboard.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
    })

# Profile View
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save(request.user)   # custom save updates both User + Profile
            messages.success(request, "Profile updated successfully.")
            return redirect("customer_dashboard")
    else:
        form = ProfileForm(instance=profile, user=request.user)  # pass user again

    return render(request, "greenpharma/profile.html", {"form": form})
