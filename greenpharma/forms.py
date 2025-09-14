from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Registration, CustomerProfile, SellerProfile, Product


# 🔹 Registration Form
class RegisterForm(UserCreationForm):
    class Meta:
        model = Registration
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Show only Customer & Seller
        self.fields['role'].choices = [
            ("Customer", "Customer"),
            ("Seller", "Seller"),
        ]


# 🔹 Login Form
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


# 🔹 Customer Profile Form
class CustomerProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 40}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, user, commit=True):
        profile = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if not self.fields['email'].disabled:
            user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile.user = user
            profile.save()
        return profile


# 🔹 Seller Profile Form (FIXED)
class SellerProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SellerProfile
        fields = ['phone', 'address', 'license_file']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 40}),
            'license_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, user, commit=True):
        profile = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Handle file upload properly
        if 'license_file' in self.files:
            profile.license_file = self.files['license_file']
            
        if commit:
            user.save()
            profile.user = user
            profile.save()
            self.save_m2m()  # Important for many-to-many relationships if any
        return profile


# 🔹 Product Form (for Sellers)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
