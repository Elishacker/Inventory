
from django import forms
from django.contrib.auth.models import User
from .models import Category, Product

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','category','price','stock','is_active']

class UserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text="Leave blank to keep current password")
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','is_staff','is_active','password']
