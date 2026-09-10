from django import forms
from django.contrib.auth import get_user_model
from .models import Product, Vendor

User = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'brand', 'category', 'active_ingredient',
            'package_unit', 'sub_unit', 'units_per_package',
            'package_price', 'sub_unit_price', 'stock_in_sub_units',
            'requires_prescription', 'description', 'image_url'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'active_ingredient': forms.Select(attrs={'class': 'form-select'}),
            'package_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Box'}),
            'sub_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Strip, Tablet'}),
            'units_per_package': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'package_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sub_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_in_sub_units': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'requires_prescription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Shipping Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")

        return cleaned_data

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'company_name', 'phone_number', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
