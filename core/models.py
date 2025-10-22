from django.db import models
from django.utils.translation import gettext_lazy as _

class SiteSettings(models.Model):
    HEADER_CHOICES = [
        ('header1', 'Header 1 - Logo Left, Menu Middle, Icons Right'),
        ('header2', 'Header 2 - Menu Left, Logo Middle, Icons Right'),
        ('header3', 'Header 3 - Centered Logo with Bottom Menu'),
        ('header4', 'Header 4 - Minimal with Side Menu'),
    ]
    FOOTER_CHOICES = [
        ('footer1', 'Footer 1 - Dark & Modern'),
        ('footer2', 'Footer 2 - Light & Clean'),
        ('footer3', 'Footer 3 - App & Newsletter'),
        ('footer4', 'Footer 4 - Bold & Primary'),
    ]

    site_name = models.CharField(max_length=100, default="My Shop")
    active_header = models.CharField(max_length=20, choices=HEADER_CHOICES, default='header1')
    active_footer = models.CharField(max_length=20, choices=FOOTER_CHOICES, default='footer1')
    support_email = models.EmailField(default="support@myshop.com")
    phone_number = models.CharField(max_length=20, default="+1234567890")
    address = models.TextField(default="Your address here")
    
    def __str__(self):
        return "Site Settings"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name}"