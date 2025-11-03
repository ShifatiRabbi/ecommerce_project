from django.db import models
from django.contrib.auth.models import User
from shop.models import Product, Category
from cart.models import Order
import uuid
from django.core.cache import cache
from django.utils.text import slugify

class Brand(models.Model):
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='brands/')
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    lead_time = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated delivery time in days")
    notes = models.TextField(blank=True, null=True)
    is_preferred = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.stock_quantity}"

class ComboOffer(models.Model):
    name = models.CharField(max_length=200)
    products = models.ManyToManyField(Product, through='ComboProduct')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ComboProduct(models.Model):
    combo = models.ForeignKey(ComboOffer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class FlashSale(models.Model):
    name = models.CharField(max_length=200)
    products = models.ManyToManyField(Product)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code

class PopUpOffer(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='popup-offers/')
    is_active = models.BooleanField(default=True)
    show_on_homepage = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return self.title

class CourierCharge(models.Model):
    area = models.CharField(max_length=100)
    charge = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.area} - {self.charge}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    department = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    join_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

class EmployeeNotification(models.Model):
    """Model for employee notifications"""
    NOTIFICATION_TYPES = [
        ('credentials', 'Login Credentials'),
        ('password_reset', 'Password Reset'),
        ('account_update', 'Account Update'),
        ('system', 'System Notification'),
        ('alert', 'Security Alert'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Employee Notification"
        verbose_name_plural = "Employee Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.employee.user.get_full_name()}"

class EmailTemplate(models.Model):
    """Model for email templates"""
    TEMPLATE_TYPES = [
        ('employee_credentials', 'Employee Credentials'),
        ('password_reset', 'Password Reset'),
        ('welcome', 'Welcome Email'),
        ('notification', 'Notification'),
        ('marketing', 'Marketing'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text="Use {{ variable_name }} for dynamic content")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    

from django.db import models
from django.urls import reverse

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    description_bn = models.TextField(blank=True, null=True)
    meta_title = models.CharField(max_length=150, blank=True, null=True)
    meta_description = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', args=[self.slug])
class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey('BlogCategory', on_delete=models.CASCADE)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # ✅ Added fields that were missing
    is_featured = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords or tags")
    focus_keywords = models.CharField(max_length=255, blank=True, help_text="SEO focus keywords")
    canonical_url = models.URLField(blank=True, null=True)

    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])

class SEOSettings(models.Model):
    page = models.CharField(max_length=100, unique=True)
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField()
    meta_keywords = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.page

class Banner(models.Model):
    POSITION_CHOICES = [
        ('home_top', 'Homepage Top'),
        ('home_middle', 'Homepage Middle'),
        ('category_top', 'Category Top'),
        ('product_top', 'Product Top'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return self.title

class CustomPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class LandingPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    template_name = models.CharField(max_length=100)
    content = models.JSONField()  # Store structured content
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class DefaultSiteSetting(models.Model):
    # Basic Information
    site_name = models.CharField(max_length=100, default="My Shop")
    site_moto = models.CharField(max_length=200, blank=True, help_text="Short tagline or motto")
    site_slogan = models.TextField(blank=True, help_text="Longer description or slogan")
    established_year = models.PositiveIntegerField(null=True, blank=True, help_text="Year business was established")
    
    # Media
    site_logo = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    site_logo_dark = models.ImageField(upload_to='site/logo/', blank=True, null=True, help_text="Logo for dark backgrounds")
    favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True)
    og_image = models.ImageField(upload_to='site/og/', blank=True, null=True, help_text="Open Graph image for social sharing")
    
    # Contact Information
    contact_email = models.EmailField(default="support@myshop.com")
    support_email = models.EmailField(blank=True, help_text="Support email address")
    sales_email = models.EmailField(blank=True, help_text="Sales email address")
    contact_phone = models.CharField(max_length=20, default="+1234567890")
    whatsapp_number = models.CharField(max_length=20, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address = models.TextField(default="123 Business Street, City, Country")
    address_short = models.CharField(max_length=100, blank=True, help_text="Short address for headers")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Map latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Map longitude")
    
    # Business Hours
    business_hours = models.TextField(blank=True, help_text="Format: Monday-Friday: 9AM-6PM")
    timezone = models.CharField(max_length=50, default="UTC", help_text="e.g., America/New_York")
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    
    # SEO & Analytics
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    google_analytics = models.TextField(blank=True, help_text="GA4 Measurement ID")
    google_tag_manager = models.TextField(blank=True)
    facebook_pixel = models.TextField(blank=True)
    google_site_verification = models.CharField(max_length=100, blank=True)
    bing_webmaster = models.CharField(max_length=100, blank=True)
    
    # Custom Code
    custom_css = models.TextField(blank=True)
    custom_js_header = models.TextField(blank=True, help_text="JavaScript added in head")
    custom_js_footer = models.TextField(blank=True, help_text="JavaScript added before closing body")
    
    # Features & Settings
    enable_guest_checkout = models.BooleanField(default=True)
    enable_user_registration = models.BooleanField(default=True)
    enable_reviews = models.BooleanField(default=True)
    enable_wishlist = models.BooleanField(default=True)
    enable_newsletter = models.BooleanField(default=True)
    
    # Currency & Regional
    default_currency = models.CharField(max_length=3, default="USD")
    currency_symbol = models.CharField(max_length=5, default="$")
    weight_unit = models.CharField(max_length=10, default="kg", choices=[('kg', 'Kilograms'), ('lb', 'Pounds')])
    dimension_unit = models.CharField(max_length=10, default="cm", choices=[('cm', 'Centimeters'), ('in', 'Inches')])
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default="We're currently performing maintenance. Please check back soon.")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Default Site Setting"
        verbose_name_plural = "Default Site Settings"

    def save(self, *args, **kwargs):
        # Clear cache when settings are updated
        cache.delete('default_site_settings')
        # Ensure only one instance exists
        if not self.pk and DefaultSiteSetting.objects.exists():
            # Update existing instance instead of creating new one
            existing = DefaultSiteSetting.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)

    def __str__(self):
        return "Default Site Settings"

    @classmethod
    def get_default_settings(cls):
        """Get default site settings with caching"""
        settings = cache.get('default_site_settings')
        if not settings:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
            cache.set('default_site_settings', settings, 60 * 15)  # Cache for 15 minutes
        return settings
    

