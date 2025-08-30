from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Product


# Home page
def home(request):
    return render(request, 'greenpharma/home.html')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, "greenpharma/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, "greenpharma/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('home')



# ---------------- PRODUCTS ----------------
def product_list(request):
    query = request.GET.get("q")
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    return render(request, "greenpharma/product_list.html", {"products": products})
