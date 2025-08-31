from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Registration Form
class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select, label="Role")  # Dropdown

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select, label="Role")  # Dropdown

