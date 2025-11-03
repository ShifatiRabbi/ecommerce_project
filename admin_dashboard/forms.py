from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from shop.models import Product, Category
from .models import *
from cart.models import Customer, CustomerCommunication, CustomerNote, BlockedCustomer
from django.utils import timezone
import re

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

class DefaultSiteSettingForm(forms.ModelForm):
    # Custom fields for better UX
    remove_site_logo = forms.BooleanField(required=False, help_text="Check to remove current logo")
    remove_favicon = forms.BooleanField(required=False, help_text="Check to remove current favicon")
    remove_og_image = forms.BooleanField(required=False, help_text="Check to remove current OG image")
    
    class Meta:
        model = DefaultSiteSetting
        fields = [
            # Basic Information
            'site_name', 'site_moto', 'site_slogan', 'established_year',
            
            # Media
            'site_logo', 'site_logo_dark', 'favicon', 'og_image',
            
            # Contact Information
            'contact_email', 'support_email', 'sales_email', 'contact_phone',
            'whatsapp_number', 'emergency_phone',
            
            # Address
            'address', 'address_short', 'latitude', 'longitude',
            
            # Business Hours
            'business_hours', 'timezone',
            
            # Social Media
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url',
            'youtube_url', 'pinterest_url', 'tiktok_url', 'whatsapp_url', 'telegram_url',
            
            # SEO & Analytics
            'meta_description', 'meta_keywords', 'google_analytics',
            'google_tag_manager', 'facebook_pixel', 'google_site_verification', 'bing_webmaster',
            
            # Custom Code
            'custom_css', 'custom_js_header', 'custom_js_footer',
            
            # Features & Settings
            'enable_guest_checkout', 'enable_user_registration', 'enable_reviews',
            'enable_wishlist', 'enable_newsletter',
            
            # Currency & Regional
            'default_currency', 'currency_symbol', 'weight_unit', 'dimension_unit',
            
            # Maintenance
            'maintenance_mode', 'maintenance_message',
        ]
        widgets = {
            'site_slogan': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'business_hours': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'rows': 3}),
            'maintenance_message': forms.Textarea(attrs={'rows': 3}),
            'custom_css': forms.Textarea(attrs={'rows': 8, 'class': 'code-editor'}),
            'custom_js_header': forms.Textarea(attrs={'rows': 6, 'class': 'code-editor'}),
            'custom_js_footer': forms.Textarea(attrs={'rows': 6, 'class': 'code-editor'}),
            'google_analytics': forms.TextInput(attrs={'placeholder': 'G-XXXXXXXXXX'}),
            'established_year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }
        help_texts = {
            'google_analytics': 'Enter your GA4 Measurement ID (e.g., G-XXXXXXXXXX)',
            'timezone': 'Select your timezone from <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones" target="_blank">TZ database</a>',
            'latitude': 'For map integration (e.g., 40.7128)',
            'longitude': 'For map integration (e.g., -74.0060)',
        }

    def clean_established_year(self):
        year = self.cleaned_data.get('established_year')
        if year and (year < 1900 or year > 2100):
            raise forms.ValidationError("Please enter a valid year between 1900 and 2100.")
        return year

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        # Basic phone validation
        if phone and not any(char.isdigit() for char in phone):
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle file removals
        if self.cleaned_data.get('remove_site_logo') and instance.site_logo:
            instance.site_logo.delete(save=False)
        if self.cleaned_data.get('remove_favicon') and instance.favicon:
            instance.favicon.delete(save=False)
        if self.cleaned_data.get('remove_og_image') and instance.og_image:
            instance.og_image.delete(save=False)
        
        if commit:
            instance.save()
        return instance

    
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

class UserForm(forms.ModelForm):
    """Form for User model (used in Employee creation)"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep current password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirm Password"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        
        return cleaned_data

class EmployeeForm(forms.ModelForm):
    """Form for Employee model"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'phone', 'address', 'position', 'salary', 
            'join_date', 'department', 'emergency_contact', 'city', 'postal_code',
            'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+880XXXXXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'join_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Sales, Marketing, IT'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact number'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'employee_id': 'Employee ID',
            'is_active': 'Active Employee',
        }
        help_texts = {
            'employee_id': 'Unique identifier for the employee',
            'join_date': 'Date when employee joined the company',
            'salary': 'Monthly salary in BDT',
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone validation for Bangladesh numbers
            if not re.match(r'^\+?880\d{10}$', phone) and not re.match(r'^01\d{9}$', phone):
                raise forms.ValidationError("Please enter a valid Bangladeshi phone number.")
        return phone
    
    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary and salary < 0:
            raise forms.ValidationError("Salary cannot be negative.")
        return salary
    
    def clean_join_date(self):
        join_date = self.cleaned_data.get('join_date')
        if join_date and join_date > timezone.now().date():
            raise forms.ValidationError("Join date cannot be in the future.")
        return join_date

class ProductForm(forms.ModelForm):
    """Form for Product model"""
    initial_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Initial stock quantity"
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'name_bn', 'slug', 'category', 'brand', 'supplier',
            'short_description', 'short_description_bn', 'description', 'description_bn',
            'price', 'compare_price', 'sku', 'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_bn': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'short_description_bn': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),
            'description_bn': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'compare_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    """Form for Category model"""
    
    class Meta:
        model = Category
        fields = [
            'name', 'name_bn', 'slug', 'parent', 'description', 'description_bn',
            'image', 'is_active', 'is_featured', 'display_order', 'meta_title', 'meta_description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_bn': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'description_bn': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class BrandForm(forms.ModelForm):
    """Form for Brand model"""
    
    class Meta:
        model = Brand
        fields = [
            'name', 'name_bn', 'logo', 'description', 'website',
            'is_active', 'is_featured', 'display_order', 'meta_title', 'meta_description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_bn': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class SupplierForm(forms.ModelForm):
    """Form for Supplier model"""
    
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'email', 'phone', 'address',
            'website', 'tax_id', 'payment_terms', 'lead_time', 'is_active', 'is_preferred', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'lead_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_preferred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Supplier.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A supplier with this email already exists.")
        return email

class BlogCategoryForm(forms.ModelForm):
    """Form for Blog Category model"""
    
    class Meta:
        model = BlogCategory
        fields = [
            'name', 'name_bn', 'slug', 'description', 'description_bn',
            'is_active', 'is_featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_bn': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'description_bn': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class BlogForm(forms.ModelForm):
    """Form for Blog model"""
    
    class Meta:
        model = Blog
        fields = [
            'title', 'slug', 'category', 'featured_image', 'excerpt', 'content',
            'tags', 'is_published', 'is_featured', 'allow_comments',
            'published_date', 'meta_title', 'meta_description', 'focus_keywords', 'canonical_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Separate tags with commas'
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'published_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'focus_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Separate keywords with commas'
            }),
            'canonical_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial published date to now if not set
        if not self.instance.pk and not self.initial.get('published_date'):
            self.initial['published_date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')

class CustomerForm(forms.ModelForm):
    """Form for Customer model"""
    
    class Meta:
        model = Customer
        fields = [
            'email', 'phone', 'full_name', 'customer_type', 'company_name', 'tax_id',
            'address', 'city', 'state', 'postal_code', 'country',
            'newsletter_subscribed', 'marketing_emails'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'newsletter_subscribed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BlockedCustomerForm(forms.ModelForm):
    """Form for Blocked Customer model"""
    
    class Meta:
        model = BlockedCustomer
        fields = [
            'email', 'reason', 'custom_reason', 'block_until', 'notes'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'custom_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about why this customer is being blocked...'
            }),
            'block_until': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes about this blocking...'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and BlockedCustomer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This customer is already blocked.")
        return email

class CustomerNoteForm(forms.ModelForm):
    """Form for Customer Note model"""
    
    class Meta:
        model = CustomerNote
        fields = [
            'customer', 'note_type', 'title', 'content', 'is_important', 'is_resolved'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'note_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter note content...'
            }),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Search and Filter Forms
class EmployeeSearchForm(forms.Form):
    """Form for employee search and filtering"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search employees...'
    }))
    status = forms.ChoiceField(required=False, choices=[
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], widget=forms.Select(attrs={'class': 'form-select'}))
    position = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Filter by position...'
    }))

class CustomerSearchForm(forms.Form):
    """Form for customer search and filtering"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search customers...'
    }))
    customer_type = forms.ChoiceField(required=False, choices=[
        ('', 'All Types'),
        ('individual', 'Individual'),
        ('business', 'Business')
    ], widget=forms.Select(attrs={'class': 'form-select'}))
    is_active = forms.ChoiceField(required=False, choices=[
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], widget=forms.Select(attrs={'class': 'form-select'}))

