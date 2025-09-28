from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from shop.models import Product, Category
from .models import *

class ProductForm(forms.ModelForm):
    initial_stock = forms.IntegerField(initial=0, min_value=0)
    additional_images = forms.ImageField(required=False, widget=forms.FileInput())
    
    class Meta:
        model = Product
        fields = ['name', 'name_bn', 'slug', 'category', 'price', 'compare_price', 
                 'short_description', 'short_description_bn', 'description', 'description_bn',
                 'sku', 'is_active', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'description_bn': forms.Textarea(attrs={'rows': 4}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_bn', 'slug', 'image', 'is_active']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'name_bn', 'logo', 'is_active']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']

class ComboOfferForm(forms.ModelForm):
    class Meta:
        model = ComboOffer
        fields = ['name', 'discount_percentage', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class FlashSaleForm(forms.ModelForm):
    class Meta:
        model = FlashSale
        fields = ['name', 'discount_percentage', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_type', 'discount_value', 'min_order_amount', 
                 'max_discount', 'start_date', 'end_date', 'usage_limit', 'is_active']

class PopUpOfferForm(forms.ModelForm):
    class Meta:
        model = PopUpOffer
        fields = ['title', 'content', 'image', 'is_active', 'show_on_homepage', 'start_date', 'end_date']

class CourierChargeForm(forms.ModelForm):
    class Meta:
        model = CourierCharge
        fields = ['area', 'charge', 'min_order_amount', 'is_active']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'phone', 'address', 'position', 'salary', 'join_date']

class BlogCategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ['name', 'slug', 'is_active']

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'slug', 'category', 'content', 'excerpt', 'featured_image', 
                 'is_published', 'meta_title', 'meta_description']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['site_name', 'site_logo', 'favicon', 'contact_email', 
                 'contact_phone', 'address', 'facebook_pixel', 
                 'google_analytics', 'google_tag_manager']

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'position', 'link', 'is_active', 'start_date', 'end_date']

class CustomPageForm(forms.ModelForm):
    class Meta:
        model = CustomPage
        fields = ['title', 'slug', 'content', 'is_active', 'meta_title', 'meta_description']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 15, 'class': 'rich-text-editor'}),
        }

class LandingPageForm(forms.ModelForm):
    class Meta:
        model = LandingPage
        fields = ['title', 'slug', 'template_name', 'content', 'is_active']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']