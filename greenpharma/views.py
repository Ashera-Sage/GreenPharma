from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm

# Home Page
def home(request):
    return render(request, 'greenpharma/home.html')

# Register View
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('role')  # Save role in first_name
            user.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'greenpharma/register.html', {'form': form})

# Login View (with role)
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')  # get role from form

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.first_name != role:
                    messages.error(request, f"You are not registered as {role}.")
                else:
                    login(request, user)
                    if role == "seller":
                        return redirect('seller_dashboard')
                    return redirect('home')
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

# Seller Dashboard (dummy page)
def seller_dashboard(request):
    return render(request, 'greenpharma/seller_dashboard.html')
