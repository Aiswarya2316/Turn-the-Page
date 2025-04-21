from django import forms
from django.contrib.auth.models import User
from .models import Buyer, Seller

# User Registration Form (Common for both Buyer & Seller)
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

# Seller Registration Form
class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['phone', 'address']

# Buyer Registration Form
class BuyerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['phone', 'address']







from django import forms
from .models import Book, ExchangeRequest

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description','image']

class ExchangeRequestForm(forms.ModelForm):
    class Meta:
        model = ExchangeRequest
        fields = ['status']
