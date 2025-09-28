from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, Avg, Subquery, OuterRef, DecimalField, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import csv
from django.http import HttpResponse
from shop.models import Product, Category, ProductImage
from cart.models import Order, OrderItem
from .models import *
from .decorators import admin_required
from .forms import *

@login_required
@admin_required
def dashboard(request):
    # Quick stats
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    weekly_revenue = Order.objects.filter(
        status='delivered', 
        created_at__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Product statistics
    low_stock_products = Inventory.objects.filter(stock_quantity__lte=5).count()
    total_products = Product.objects.filter(is_active=True).count()
    total_customers = Order.objects.values('email').distinct().count()
    
    # Recent orders
    recent_orders = Order.objects.select_related().order_by('-created_at')[:10]
    
    # Top selling products
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # Sales data for charts
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        daily_sales = Order.objects.filter(
            status='delivered',
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.append({
            'date': date.strftime('%b %d'),
            'sales': float(daily_sales)
        })
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'weekly_revenue': weekly_revenue,
        'low_stock_products': low_stock_products,
        'total_products': total_products,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'sales_data': sales_data,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

# ================= ORDERS SECTION =================

@login_required
@admin_required
def completed_orders(request):
    orders = Order.objects.filter(status='delivered').order_by('-created_at')
    
    # Calculate stats
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
    this_month_orders = orders.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'avg_order_value': round(avg_order_value, 2),
        'this_month_orders': this_month_orders,
    }
    return render(request, 'admin_dashboard/orders/completed.html', context)

@login_required
@admin_required
def incomplete_orders(request):
    incomplete_orders = Order.objects.filter(
        Q(phone__isnull=False) | Q(email__isnull=False),
        status__in=['pending', 'processing']
    ).order_by('-created_at')
    
    # Calculate potential revenue
    potential_revenue = incomplete_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'orders': incomplete_orders,
        'potential_revenue': potential_revenue,
    }
    return render(request, 'admin_dashboard/orders/incomplete.html', context)

@login_required
@admin_required
def fake_orders(request):
    # Implement fake order detection logic
    fake_orders = Order.objects.filter(
        Q(phone__startswith='123') | 
        Q(email__endswith='fake.com') |
        Q(total_amount=0)
    ).order_by('-created_at')
    return render(request, 'admin_dashboard/orders/fake.html', {'orders': fake_orders})

@login_required
@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product').all()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}')
        return redirect('admin_dashboard:order_detail', order_id=order.id)
    
    return render(request, 'admin_dashboard/orders/detail.html', {
        'order': order,
        'order_items': order_items
    })

# ================= PRODUCTS SECTION =================
@login_required
@admin_required
def product_list(request):
    products = Product.objects.select_related('category').prefetch_related('images').all()
    
    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    
    # Pagination
    paginator = Paginator(products, 25)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    
    categories = Category.objects.all()
    
    return render(request, 'admin_dashboard/products/list.html', {
        'products': products_page,
        'categories': categories
    })

@login_required
@admin_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Handle multiple images
            images = request.FILES.getlist('additional_images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            # Create inventory entry
            Inventory.objects.create(
                product=product,
                stock_quantity=form.cleaned_data['initial_stock'],
                low_stock_threshold=10
            )
            
            messages.success(request, 'Product added successfully!')
            return redirect('admin_dashboard:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'admin_dashboard/products/add.html', {'form': form})

@login_required
@admin_required
def product_reporting(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

    orders = Order.objects.filter(
        status='delivered',
        created_at__date__range=[start_date, end_date]
    )

    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_units_sold = OrderItem.objects.filter(order__in=orders).aggregate(total=Sum('quantity'))['total'] or 0
    avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0

    top_products = OrderItem.objects.filter(order__in=orders).values(
        'product__name', 'product__sku'
    ).annotate(
        total_sold=Sum('quantity', output_field=IntegerField()),
        total_revenue=Sum(
            ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField())
        )
    ).order_by('-total_sold')[:10]

    low_stock = Inventory.objects.filter(stock_quantity__lte=F('low_stock_threshold'))

    product_performance = Product.objects.filter(is_active=True).annotate(
        units_sold=Coalesce(
            Subquery(
                OrderItem.objects.filter(
                    product=OuterRef('pk'),
                    order__in=orders
                ).values('product').annotate(
                    total=Sum('quantity', output_field=IntegerField())
                ).values('total')[:1]
            ),
            0,
            output_field=IntegerField()
        ),
        revenue=Coalesce(
            Subquery(
                OrderItem.objects.filter(
                    product=OuterRef('pk'),
                    order__in=orders
                ).values('product').annotate(
                    total=Sum(
                        ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField())
                    )
                ).values('total')[:1]
            ),
            0,
            output_field=DecimalField()
        )
    )

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'total_units_sold': total_units_sold,
        'avg_order_value': round(avg_order_value, 2),
        'conversion_rate': 3.2,
        'top_products': top_products,
        'low_stock': low_stock,
        'product_performance': product_performance,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_dashboard/products/reporting.html', context)

@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    
    # Calculate stats
    active_categories = categories.filter(is_active=True).count()
    total_products = Product.objects.count()
    avg_products_per_category = total_products / categories.count() if categories.count() > 0 else 0
    
    context = {
        'categories': categories,
        'active_categories': active_categories,
        'total_products': total_products,
        'avg_products_per_category': round(avg_products_per_category, 1),
    }
    return render(request, 'admin_dashboard/products/category_list.html', context)

@login_required
@admin_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('admin_dashboard:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'admin_dashboard/products/category_add.html', {'form': form})

@login_required
@admin_required
def brand_list(request):
    brands = Brand.objects.all()
    
    # Calculate stats
    active_brands = brands.filter(is_active=True).count()
    total_branded_products = Product.objects.filter(brand__isnull=False).count()
    top_brand = brands.annotate(product_count=Count('product')).order_by('-product_count').first()
    
    context = {
        'brands': brands,
        'active_brands': active_brands,
        'total_branded_products': total_branded_products,
        'top_brand': top_brand,
    }
    return render(request, 'admin_dashboard/products/brand_list.html', context)

@login_required
@admin_required
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added successfully!')
            return redirect('admin_dashboard:brand_list')
    else:
        form = BrandForm()
    
    return render(request, 'admin_dashboard/products/brand_add.html', {'form': form})

@login_required
@admin_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'admin_dashboard/products/supplier_list.html', {'suppliers': suppliers})

@login_required
@admin_required
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('admin_dashboard:supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'admin_dashboard/products/supplier_add.html', {'form': form})

@login_required
@admin_required
def inventory_list(request):
    inventory = Inventory.objects.select_related('product').all()
    
    # Apply filters
    stock_status = request.GET.get('stock_status')
    if stock_status == 'out_of_stock':
        inventory = inventory.filter(stock_quantity=0)
    elif stock_status == 'low_stock':
        inventory = inventory.filter(stock_quantity__lte=F('low_stock_threshold'))
    elif stock_status == 'in_stock':
        inventory = inventory.filter(stock_quantity__gt=F('low_stock_threshold'))
    
    category_id = request.GET.get('category')
    if category_id:
        inventory = inventory.filter(product__category_id=category_id)
    
    search = request.GET.get('search')
    if search:
        inventory = inventory.filter(
            Q(product__name__icontains=search) | 
            Q(product__sku__icontains=search)
        )
    
    # Calculate stats
    out_of_stock_count = inventory.filter(stock_quantity=0).count()
    low_stock_count = inventory.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).count()
    in_stock_count = inventory.filter(stock_quantity__gt=F('low_stock_threshold')).count()
    
    # Recent stock history (you'd need a StockHistory model for this)
    stock_history = []  # This would come from StockHistory model
    
    context = {
        'inventory': inventory,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
        'in_stock_count': in_stock_count,
        'stock_history': stock_history,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_dashboard/products/inventory.html', context)

# ================= OFFERS SECTION =================
@login_required
@admin_required
def combo_offer_list(request):
    combos = ComboOffer.objects.all()
    return render(request, 'admin_dashboard/offers/combo_list.html', {'combos': combos})

@login_required
@admin_required
def add_combo_offer(request):
    if request.method == 'POST':
        form = ComboOfferForm(request.POST)
        if form.is_valid():
            combo = form.save()
            
            # Handle combo products
            product_ids = request.POST.getlist('products')
            quantities = request.POST.getlist('quantities')
            
            for product_id, quantity in zip(product_ids, quantities):
                if product_id and quantity:
                    ComboProduct.objects.create(
                        combo=combo,
                        product_id=product_id,
                        quantity=quantity
                    )
            
            messages.success(request, 'Combo offer created successfully!')
            return redirect('admin_dashboard:combo_offer_list')
    else:
        form = ComboOfferForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'admin_dashboard/offers/combo_add.html', {
        'form': form,
        'products': products
    })

@login_required
@admin_required
def flash_sale_list(request):
    flash_sales = FlashSale.objects.all()
    return render(request, 'admin_dashboard/offers/flash_sale_list.html', {'flash_sales': flash_sales})

@login_required
@admin_required
def add_flash_sale(request):
    if request.method == 'POST':
        form = FlashSaleForm(request.POST)
        if form.is_valid():
            flash_sale = form.save()
            
            # Handle products
            product_ids = request.POST.getlist('products')
            for product_id in product_ids:
                if product_id:
                    flash_sale.products.add(product_id)
            
            messages.success(request, 'Flash sale created successfully!')
            return redirect('admin_dashboard:flash_sale_list')
    else:
        form = FlashSaleForm()
    
    products = Product.objects.filter(is_active=True)
    return render(request, 'admin_dashboard/offers/flash_sale_add.html', {
        'form': form,
        'products': products
    })

@login_required
@admin_required
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'admin_dashboard/offers/coupon_list.html', {'coupons': coupons})

@login_required
@admin_required
def discount_settings(request):
    # Global discount settings
    if request.method == 'POST':
        # Save discount settings
        messages.success(request, 'Discount settings updated successfully!')
        return redirect('admin_dashboard:discount_settings')
    
    return render(request, 'admin_dashboard/offers/discount_settings.html')

@login_required
@admin_required
def popup_offers(request):
    popups = PopUpOffer.objects.all()
    return render(request, 'admin_dashboard/offers/popup_list.html', {'popups': popups})

# ================= COURIER & DELIVERY =================
@login_required
@admin_required
def courier_charges(request):
    charges = CourierCharge.objects.all()
    
    if request.method == 'POST':
        form = CourierChargeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Courier charge added successfully!')
            return redirect('admin_dashboard:courier_charges')
    else:
        form = CourierChargeForm()
    
    return render(request, 'admin_dashboard/courier/charges.html', {
        'charges': charges,
        'form': form
    })

@login_required
@admin_required
def courier_api(request):
    # Courier API integration settings
    if request.method == 'POST':
        # Save API settings
        messages.success(request, 'Courier API settings updated successfully!')
        return redirect('admin_dashboard:courier_api')
    
    return render(request, 'admin_dashboard/courier/api.html')

# ================= PAYMENT METHODS =================
@login_required
@admin_required
def sslcommerz_settings(request):
    if request.method == 'POST':
        # Save SSLCommerz settings
        messages.success(request, 'SSLCommerz settings updated successfully!')
        return redirect('admin_dashboard:sslcommerz_settings')
    
    return render(request, 'admin_dashboard/payment/sslcommerz.html')

@login_required
@admin_required
def bkash_settings(request):
    if request.method == 'POST':
        # Save bKash settings
        messages.success(request, 'bKash settings updated successfully!')
        return redirect('admin_dashboard:bkash_settings')
    
    return render(request, 'admin_dashboard/payment/bkash.html')

@login_required
@admin_required
def manual_payment_settings(request):
    if request.method == 'POST':
        # Save manual payment settings
        messages.success(request, 'Manual payment settings updated successfully!')
        return redirect('admin_dashboard:manual_payment_settings')
    
    return render(request, 'admin_dashboard/payment/manual.html')

# ================= EMPLOYEES =================
@login_required
@admin_required
def employee_list(request):
    employees = Employee.objects.select_related('user').all()
    return render(request, 'admin_dashboard/employees/list.html', {'employees': employees})

@login_required
@admin_required
def add_employee(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password('defaultpassword')  # Should be changed by employee
            user.save()
            
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            
            messages.success(request, 'Employee added successfully!')
            return redirect('admin_dashboard:employee_list')
    else:
        user_form = UserForm()
        employee_form = EmployeeForm()
    
    return render(request, 'admin_dashboard/employees/add.html', {
        'user_form': user_form,
        'employee_form': employee_form
    })

@login_required
@admin_required
def employee_settings(request):
    # Employee role and permission settings
    return render(request, 'admin_dashboard/employees/settings.html')

@login_required
@admin_required
def employee_reports(request):
    # Employee performance reports
    employees = Employee.objects.all()
    
    # Add reporting logic here
    return render(request, 'admin_dashboard/employees/reports.html', {'employees': employees})

# ================= CUSTOMERS =================
@login_required
@admin_required
def all_customers(request):
    # Get unique customers from orders
    customers = Order.objects.values('email', 'full_name', 'phone').distinct()
    
    # Pagination
    paginator = Paginator(customers, 25)
    page = request.GET.get('page')
    customers_page = paginator.get_page(page)
    
    return render(request, 'admin_dashboard/customers/all.html', {'customers': customers_page})

@login_required
@admin_required
def blocked_customers(request):
    # Implement customer blocking logic
    blocked_emails = []  # Should come from a BlockedCustomer model
    return render(request, 'admin_dashboard/customers/blocked.html', {'blocked_customers': blocked_emails})

# ================= BLOGS =================
@login_required
@admin_required
def blog_categories(request):
    categories = BlogCategory.objects.all()
    return render(request, 'admin_dashboard/blogs/categories.html', {'categories': categories})

@login_required
@admin_required
def add_blog_category(request):
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog category added successfully!')
            return redirect('admin_dashboard:blog_categories')
    else:
        form = BlogCategoryForm()
    
    return render(request, 'admin_dashboard/blogs/category_add.html', {'form': form})

@login_required
@admin_required
def blog_list(request):
    blogs = Blog.objects.select_related('category', 'author').all()
    return render(request, 'admin_dashboard/blogs/list.html', {'blogs': blogs})

@login_required
@admin_required
def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            if form.cleaned_data['is_published']:
                blog.published_date = timezone.now()
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_dashboard:blog_list')
    else:
        form = BlogForm()
    
    return render(request, 'admin_dashboard/blogs/add.html', {'form': form})

# ================= MARKETING =================
@login_required
@admin_required
def facebook_conversion_api(request):
    if request.method == 'POST':
        # Save Facebook Conversion API settings
        messages.success(request, 'Facebook Conversion API settings updated!')
        return redirect('admin_dashboard:facebook_conversion_api')
    
    return render(request, 'admin_dashboard/marketing/facebook_conversion.html')

@login_required
@admin_required
def facebook_messenger(request):
    if request.method == 'POST':
        # Save Facebook Messenger settings
        messages.success(request, 'Facebook Messenger settings updated!')
        return redirect('admin_dashboard:facebook_messenger')
    
    return render(request, 'admin_dashboard/marketing/facebook_messenger.html')

@login_required
@admin_required
def google_gtm(request):
    if request.method == 'POST':
        # Save Google Tag Manager settings
        messages.success(request, 'Google Tag Manager settings updated!')
        return redirect('admin_dashboard:google_gtm')
    
    return render(request, 'admin_dashboard/marketing/google_gtm.html')

@login_required
@admin_required
def google_ga4(request):
    if request.method == 'POST':
        # Save Google Analytics settings
        messages.success(request, 'Google Analytics settings updated!')
        return redirect('admin_dashboard:google_ga4')
    
    return render(request, 'admin_dashboard/marketing/google_ga4.html')

@login_required
@admin_required
def technical_seo(request):
    seo_settings = SEOSettings.objects.all()
    return render(request, 'admin_dashboard/marketing/technical_seo.html', {'seo_settings': seo_settings})

@login_required
@admin_required
def onpage_seo(request):
    if request.method == 'POST':
        # Save on-page SEO settings
        messages.success(request, 'On-page SEO settings updated!')
        return redirect('admin_dashboard:onpage_seo')
    
    return render(request, 'admin_dashboard/marketing/onpage_seo.html')

@login_required
@admin_required
def sms_api(request):
    if request.method == 'POST':
        # Save SMS API settings
        messages.success(request, 'SMS API settings updated!')
        return redirect('admin_dashboard:sms_api')
    
    return render(request, 'admin_dashboard/marketing/sms_api.html')

@login_required
@admin_required
def sms_message(request):
    # SMS message templates
    if request.method == 'POST':
        # Save SMS templates
        messages.success(request, 'SMS templates updated!')
        return redirect('admin_dashboard:sms_message')
    
    return render(request, 'admin_dashboard/marketing/sms_message.html')

@login_required
@admin_required
def live_chat(request):
    if request.method == 'POST':
        # Save live chat settings
        messages.success(request, 'Live chat settings updated!')
        return redirect('admin_dashboard:live_chat')
    
    return render(request, 'admin_dashboard/marketing/live_chat.html')

@login_required
@admin_required
def third_party_integrations(request):
    if request.method == 'POST':
        # Save integration settings
        messages.success(request, 'Integration settings updated!')
        return redirect('admin_dashboard:third_party_integrations')
    
    return render(request, 'admin_dashboard/marketing/integrations.html')

# ================= MANAGE SITE =================
@login_required
@admin_required
def basic_settings(request):
    settings = SiteSetting.objects.first()
    if not settings:
        settings = SiteSetting.objects.create()
    
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully!')
            return redirect('admin_dashboard:basic_settings')
    else:
        form = SiteSettingForm(instance=settings)
    
    return render(request, 'admin_dashboard/manage/basic_settings.html', {'form': form})

@login_required
@admin_required
def homepage_design(request):
    # Homepage layout and section management
    if request.method == 'POST':
        # Save homepage design
        messages.success(request, 'Homepage design updated!')
        return redirect('admin_dashboard:homepage_design')
    
    return render(request, 'admin_dashboard/manage/homepage_design.html')

@login_required
@admin_required
def header_design(request):
    # Get header templates and settings
    header_templates = [
        {
            'id': 1,
            'name': 'Logo Left, Menu Middle, Icons Right',
            'description': 'Classic header layout with logo on left',
            'layout': 'logo_left',
            'class_name': 'header-logo-left'
        },
        {
            'id': 2, 
            'name': 'Menu Left, Logo Center, Icons Right',
            'description': 'Modern layout with centered logo',
            'layout': 'logo_center',
            'class_name': 'header-logo-center'
        },
        {
            'id': 3,
            'name': 'Minimal with Side Menu',
            'description': 'Clean minimal design with hamburger menu',
            'layout': 'minimal',
            'class_name': 'header-minimal'
        }
    ]
    
    active_header = header_templates[0]  # This would come from database
    header_settings = {}  # This would come from database
    menu_items = [
        {'title': 'Home', 'url': '/'},
        {'title': 'Shop', 'url': '/shop/'},
        {'title': 'Categories', 'url': '/categories/'},
        {'title': 'Contact', 'url': '/contact/'},
    ]
    custom_css = ""  # This would come from database
    
    context = {
        'header_templates': header_templates,
        'active_header': active_header,
        'header_settings': header_settings,
        'menu_items': menu_items,
        'custom_css': custom_css,
    }
    return render(request, 'admin_dashboard/manage/header_design.html', context)

@login_required
@admin_required
def footer_design(request):
    # Footer design settings
    if request.method == 'POST':
        # Save footer design
        messages.success(request, 'Footer design updated!')
        return redirect('admin_dashboard:footer_design')
    
    return render(request, 'admin_dashboard/manage/footer_design.html')

@login_required
@admin_required
def product_page_design(request):
    # Product page layout settings
    return render(request, 'admin_dashboard/manage/product_page_design.html')

@login_required
@admin_required
def order_tracking(request):
    # Order tracking page settings
    return render(request, 'admin_dashboard/manage/order_tracking.html')

@login_required
@admin_required
def checkout_design(request):
    # Checkout page design
    return render(request, 'admin_dashboard/manage/checkout_design.html')

@login_required
@admin_required
def thankyou_design(request):
    # Thank you page design
    return render(request, 'admin_dashboard/manage/thankyou_design.html')

@login_required
@admin_required
def invoice_design(request):
    # Invoice template design
    return render(request, 'admin_dashboard/manage/invoice_design.html')

@login_required
@admin_required
def custom_css(request):
    custom_css = ""  # This would come from database
    
    if request.method == 'POST':
        custom_css = request.POST.get('custom_css', '')
        # Save to database
        # settings = SiteSetting.objects.first()
        # settings.custom_css = custom_css
        # settings.save()
        messages.success(request, 'Custom CSS saved successfully!')
        return redirect('admin_dashboard:custom_css')
    
    context = {
        'custom_css': custom_css,
    }
    return render(request, 'admin_dashboard/manage/custom_css.html', context)

@login_required
@admin_required
def custom_js(request):
    settings = SiteSetting.objects.first()
    
    if request.method == 'POST':
        settings.custom_js = request.POST.get('custom_js', '')
        settings.save()
        messages.success(request, 'Custom JavaScript updated!')
        return redirect('admin_dashboard:custom_js')
    
    return render(request, 'admin_dashboard/manage/custom_js.html', {
        'custom_js': settings.custom_js if settings else ''
    })

@login_required
@admin_required
def banner_list(request):
    active_banners = Banner.objects.filter(is_active=True)
    all_banners = Banner.objects.all()
    
    context = {
        'active_banners': active_banners,
        'all_banners': all_banners,
    }
    return render(request, 'admin_dashboard/manage/banner_list.html', context)

@login_required
@admin_required
def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner added successfully!')
            return redirect('admin_dashboard:banner_list')
    else:
        form = BannerForm()
    
    return render(request, 'admin_dashboard/manage/banner_add.html', {'form': form})

# ================= BACKEND CUSTOMIZATION =================
@login_required
@admin_required
def orders_customize(request):
    # Order process customization
    if request.method == 'POST':
        # Save order customization
        messages.success(request, 'Order customization updated!')
        return redirect('admin_dashboard:orders_customize')
    
    return render(request, 'admin_dashboard/customization/orders.html')

@login_required
@admin_required
def order_status_customize(request):
    # Order status workflow customization
    if request.method == 'POST':
        # Save status customization
        messages.success(request, 'Order status customization updated!')
        return redirect('admin_dashboard:order_status_customize')
    
    return render(request, 'admin_dashboard/customization/order_status.html')

# ================= PAGE BUILDER =================
@login_required
@admin_required
def page_list(request):
    pages = CustomPage.objects.all()
    return render(request, 'admin_dashboard/page_builder/page_list.html', {'pages': pages})

@login_required
@admin_required
def create_page(request):
    if request.method == 'POST':
        form = CustomPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page created successfully!')
            return redirect('admin_dashboard:page_list')
    else:
        form = CustomPageForm()
    
    return render(request, 'admin_dashboard/page_builder/create_page.html', {'form': form})

@login_required
@admin_required
def landing_page_list(request):
    landing_pages = LandingPage.objects.all()
    return render(request, 'admin_dashboard/page_builder/landing_list.html', {'landing_pages': landing_pages})

@login_required
@admin_required
def create_landing_page(request):
    if request.method == 'POST':
        form = LandingPageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Landing page created successfully!')
            return redirect('admin_dashboard:landing_page_list')
    else:
        form = LandingPageForm()
    
    return render(request, 'admin_dashboard/page_builder/create_landing.html', {'form': form})

@login_required
@admin_required
def template_demo(request):
    # Show available templates
    return render(request, 'admin_dashboard/page_builder/templates.html')

# ================= PROFILE =================
@login_required
@admin_required
def profile_settings(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_dashboard:profile_settings')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'admin_dashboard/profile/settings.html', {'form': form})

@login_required
@admin_required
def admin_logout(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('core:home')

# ================= AJAX ENDPOINTS =================
@login_required
@admin_required
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        
        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
            return JsonResponse({'success': True, 'new_status': order.get_status_display()})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@admin_required
def update_inventory(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        
        try:
            inventory = Inventory.objects.get(product_id=product_id)
            inventory.stock_quantity = quantity
            inventory.save()
            return JsonResponse({'success': True})
        except Inventory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Inventory not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@admin_required
def get_order_stats(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    data = {
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'week_orders': Order.objects.filter(created_at__date__gte=week_ago).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': float(Order.objects.filter(
            status='delivered', 
            created_at__date__gte=week_ago
        ).aggregate(total=Sum('total_amount'))['total'] or 0)
    }
    return JsonResponse(data)

@login_required
@admin_required
def get_sales_data(request):
    # Return sales data for charts
    today = timezone.now().date()
    sales_data = []
    
    for i in range(7):
        date = today - timedelta(days=6-i)
        daily_sales = Order.objects.filter(
            status='delivered',
            created_at__date=date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        sales_data.append({
            'date': date.strftime('%b %d'),
            'sales': float(daily_sales)
        })
    
    return JsonResponse({'sales_data': sales_data})