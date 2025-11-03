from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.cache import cache
from django.utils.text import slugify

class SiteSettings(models.Model):
    HEADER_CHOICES = [
        ('header1', 'Header 1 - Classic'),
        ('header2', 'Header 2 - Modern'),
        ('header3', 'Header 3 - Minimal'),
        ('header4', 'Header 4 - Centered'),
    ]
    FOOTER_CHOICES = [
        ('footer1', 'Footer 1 - Dark Modern'),
        ('footer2', 'Footer 2 - Light Clean'),
        ('footer3', 'Footer 3 - App Style'),
        ('footer4', 'Footer 4 - Bold Primary'),
    ]

    site_name = models.CharField(max_length=100, default="My Shop")
    site_logo = models.ImageField(upload_to='site/logo/', blank=True, null=True)
    site_description = models.TextField(blank=True, default="Your trusted ecommerce partner")
    favicon = models.ImageField(upload_to='site/favicon/', blank=True, null=True)
    
    active_header = models.CharField(max_length=20, choices=HEADER_CHOICES, default='header1')
    active_footer = models.CharField(max_length=20, choices=FOOTER_CHOICES, default='footer1')
    
    # Header Settings
    sticky_header = models.BooleanField(default=True)
    header_background = models.CharField(max_length=7, default='#ffffff')
    header_text_color = models.CharField(max_length=7, default='#333333')
    header_height = models.PositiveIntegerField(default=80)
    logo_size = models.PositiveIntegerField(default=40)
    
    # Footer Settings
    footer_background = models.CharField(max_length=7, default='#2c3e50')
    footer_text_color = models.CharField(max_length=7, default='#ffffff')
    
    # Contact Info
    contact_email = models.EmailField(default="support@myshop.com")
    contact_phone = models.CharField(max_length=20, default="+1234567890")
    address = models.TextField(default="123 Business Street, City, Country")
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Custom Code
    custom_css = models.TextField(blank=True)
    custom_js = models.TextField(blank=True)
    
    # SEO
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        # Clear cache when settings are updated
        cache.delete('site_settings')
        super().save(*args, **kwargs)

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_settings(cls):
        """Get site settings with caching"""
        settings = cache.get('site_settings')
        if not settings:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
            cache.set('site_settings', settings, 60 * 15)  # Cache for 15 minutes
        return settings

class HeaderTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_name = models.CharField(max_length=100, help_text="Template file name without extension")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='headers/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Header Template"
        verbose_name_plural = "Header Templates"


class FooterTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_name = models.CharField(max_length=100, help_text="Template file name without extension")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='footers/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Footer Template"
        verbose_name_plural = "Footer Templates"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name}"