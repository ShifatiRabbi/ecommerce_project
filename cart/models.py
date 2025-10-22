from django.db import models
from shop.models import Product
from django.contrib.auth.models import User
from django.utils import timezone

# Customer Related Models
class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    company_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Bangladesh')
    
    # Customer Preferences
    preferences = models.JSONField(default=dict, blank=True)  # Store preferences as JSON
    newsletter_subscribed = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=True)
    
    # Statistics
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    first_order_date = models.DateTimeField(null=True, blank=True)
    
    # Customer Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_blocked']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})" if self.full_name else self.email
    
    @property
    def order_count(self):
        return self.orders.count()
    
    @property
    def average_order_value(self):
        if self.total_orders > 0:
            return self.total_spent / self.total_orders
        return 0
    
    def update_customer_stats(self):
        """Update customer statistics from orders"""
        from django.db.models import Count, Sum, Max, Min
        from admin_dashboard.models import Order
        
        orders = Order.objects.filter(email=self.email)
        
        self.total_orders = orders.count()
        self.total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        if orders.exists():
            self.last_order_date = orders.aggregate(last=Max('created_at'))['last']
            self.first_order_date = orders.aggregate(first=Min('created_at'))['first']
        
        self.save()

class CustomerNote(models.Model):
    NOTE_TYPE_CHOICES = [
        ('general', 'General Note'),
        ('support', 'Support Ticket'),
        ('complaint', 'Complaint'),
        ('praise', 'Praise'),
        ('follow_up', 'Follow Up'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_important = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Customer Note"
        verbose_name_plural = "Customer Notes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.customer.email}"

class BlockedCustomer(models.Model):
    BLOCK_REASON_CHOICES = [
        ('fraud', 'Fraudulent Activity'),
        ('abuse', 'Abusive Behavior'),
        ('spam', 'Spam Account'),
        ('chargeback', 'Frequent Chargebacks'),
        ('tos_violation', 'Terms of Service Violation'),
        ('payment_issue', 'Payment Issues'),
        ('other', 'Other'),
    ]
    
    email = models.EmailField(unique=True)
    reason = models.CharField(max_length=50, choices=BLOCK_REASON_CHOICES, default='other')
    custom_reason = models.TextField(blank=True, help_text="Additional details about the blocking reason")
    
    # Blocking Information
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_customers')
    blocked_at = models.DateTimeField(auto_now_add=True)
    block_until = models.DateTimeField(null=True, blank=True, help_text="Leave empty for permanent block")
    
    # Additional Information
    previous_orders_count = models.PositiveIntegerField(default=0)
    total_amount_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, help_text="Internal notes about the blocking")
    
    # Status
    is_active = models.BooleanField(default=True)
    auto_unblock_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Blocked Customer"
        verbose_name_plural = "Blocked Customers"
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['blocked_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.email} (Blocked)"
    
    @property
    def is_permanent(self):
        return self.block_until is None
    
    @property
    def is_expired(self):
        if self.block_until and timezone.now() > self.block_until:
            return True
        return False
    
    @property
    def display_reason(self):
        if self.custom_reason:
            return self.custom_reason
        return self.get_reason_display()
    
    def save(self, *args, **kwargs):
        # Update customer stats before blocking
        if not self.pk:  # Only on creation
            try:
                customer = Customer.objects.get(email=self.email)
                self.previous_orders_count = customer.total_orders
                self.total_amount_spent = customer.total_spent
                
                # Mark customer as blocked
                customer.is_blocked = True
                customer.save()
            except Customer.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

class CustomerCommunication(models.Model):
    COMMUNICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('chat', 'Live Chat'),
        ('ticket', 'Support Ticket'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='communications')
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Sender Information
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Response tracking
    response_received = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True)
    
    # Metadata
    template_used = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=100, blank=True)  # For email service provider IDs
    
    class Meta:
        verbose_name = "Customer Communication"
        verbose_name_plural = "Customer Communications"
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.communication_type} to {self.customer.email}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    # Add customer relationship
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    email = models.EmailField()  # Keep email for guest orders
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"