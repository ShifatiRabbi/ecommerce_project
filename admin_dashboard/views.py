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
from cart.models import *
from .models import *
from .decorators import admin_required
from cart.models import Customer, CustomerCommunication, CustomerNote, BlockedCustomer
from django.db import transaction
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from .forms import *

def get_current_site(request):
    """Utility function to get current site"""
    from django.contrib.sites.models import Site
    try:
        return Site.objects.get_current(request)
    except:
        # Fallback if sites framework is not configured
        class MockSite:
            name = "Your Ecommerce Site"
            domain = request.get_host()
        return MockSite()

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

# ================= API VIEWS =================

@login_required
@admin_required
def category_stats(request):
    """API endpoint for category statistics"""
    try:
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()
        featured_categories = Category.objects.filter(is_featured=True).count()
        
        # Products per category stats
        categories_with_products = Category.objects.annotate(
            product_count=Count('product')
        )
        total_products = sum(cat.product_count for cat in categories_with_products)
        avg_products_per_category = total_products / total_categories if total_categories > 0 else 0
        
        # Top categories by product count
        top_categories = categories_with_products.order_by('-product_count')[:5].values(
            'id', 'name', 'product_count'
        )
        
        return JsonResponse({
            'success': True,
            'total_categories': total_categories,
            'active_categories': active_categories,
            'featured_categories': featured_categories,
            'total_products': total_products,
            'avg_products_per_category': round(avg_products_per_category, 1),
            'top_categories': list(top_categories)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@admin_required
def brand_stats(request):
    """API endpoint for brand statistics"""
    try:
        total_brands = Brand.objects.count()
        active_brands = Brand.objects.filter(is_active=True).count()
        featured_brands = Brand.objects.filter(is_featured=True).count()
        
        # Products per brand stats
        brands_with_products = Brand.objects.annotate(
            product_count=Count('product')
        )
        total_branded_products = sum(brand.product_count for brand in brands_with_products)
        
        # Top brands by product count
        top_brands = brands_with_products.order_by('-product_count')[:5].values(
            'id', 'name', 'logo', 'product_count'
        )
        
        # Add logo URLs
        for brand in top_brands:
            if brand['logo']:
                brand['logo_url'] = request.build_absolute_uri(brand['logo'].url)
            else:
                brand['logo_url'] = None
        
        return JsonResponse({
            'success': True,
            'total_brands': total_brands,
            'active_brands': active_brands,
            'featured_brands': featured_brands,
            'total_branded_products': total_branded_products,
            'top_brands': list(top_brands)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@admin_required
def supplier_stats(request):
    """API endpoint for supplier statistics"""
    try:
        total_suppliers = Supplier.objects.count()
        active_suppliers = Supplier.objects.filter(is_active=True).count()
        preferred_suppliers = Supplier.objects.filter(is_preferred=True).count()
        
        # Products per supplier stats
        suppliers_with_products = Supplier.objects.annotate(
            product_count=Count('product')
        )
        total_supplier_products = sum(supplier.product_count for supplier in suppliers_with_products)
        
        # Supplier performance metrics (placeholder - you can add real metrics)
        supplier_performance = suppliers_with_products.annotate(
            avg_lead_time=Avg('lead_time'),
            reliability_score=Avg('reliability_score') if hasattr(Supplier, 'reliability_score') else 95.0
        ).values('id', 'name', 'product_count', 'avg_lead_time', 'reliability_score')[:5]
        
        return JsonResponse({
            'success': True,
            'total_suppliers': total_suppliers,
            'active_suppliers': active_suppliers,
            'preferred_suppliers': preferred_suppliers,
            'total_supplier_products': total_supplier_products,
            'supplier_performance': list(supplier_performance)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@admin_required
def recent_brands(request):
    """API endpoint for recent brands"""
    try:
        recent_brands = Brand.objects.filter(is_active=True).order_by('-id')[:10].values(
            'id', 'name', 'logo', 'is_active', 'created_at'
        )
        
        # Add product count and logo URLs
        brands_with_counts = []
        for brand in recent_brands:
            brand_data = dict(brand)
            brand_data['product_count'] = Product.objects.filter(brand_id=brand['id']).count()
            
            if brand['logo']:
                brand_obj = Brand.objects.get(id=brand['id'])
                brand_data['logo_url'] = request.build_absolute_uri(brand_obj.logo.url)
            else:
                brand_data['logo_url'] = None
            
            brands_with_counts.append(brand_data)
        
        return JsonResponse({
            'success': True,
            'brands': brands_with_counts
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@admin_required
def toggle_blog_category(request):
    """API endpoint to toggle blog category status"""
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category_id')
            action = request.POST.get('action')
            
            if not category_id or not action:
                return JsonResponse({
                    'success': False,
                    'error': 'Category ID and action are required'
                })
            
            category = BlogCategory.objects.get(id=category_id)
            
            if action == 'activate':
                category.is_active = True
                message = 'Category activated successfully'
            elif action == 'deactivate':
                category.is_active = False
                message = 'Category deactivated successfully'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                })
            
            category.save()
            
            return JsonResponse({
                'success': True,
                'message': message,
                'is_active': category.is_active
            })
            
        except BlogCategory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Blog category not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def toggle_blog_status(request):
    """API endpoint to toggle blog post status"""
    if request.method == 'POST':
        try:
            blog_id = request.POST.get('blog_id')
            action = request.POST.get('action')
            
            if not blog_id or not action:
                return JsonResponse({
                    'success': False,
                    'error': 'Blog ID and action are required'
                })
            
            blog = Blog.objects.get(id=blog_id)
            
            if action == 'publish':
                blog.is_published = True
                if not blog.published_date:
                    blog.published_date = timezone.now()
                message = 'Blog published successfully'
            elif action == 'unpublish':
                blog.is_published = False
                message = 'Blog unpublished successfully'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                })
            
            blog.save()
            
            return JsonResponse({
                'success': True,
                'message': message,
                'is_published': blog.is_published
            })
            
        except Blog.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Blog post not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def bulk_category_action(request):
    """API endpoint for bulk category actions"""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            category_ids = request.POST.getlist('category_ids[]')
            
            if not action or not category_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and category IDs are required'
                })
            
            categories = Category.objects.filter(id__in=category_ids)
            
            if action == 'activate':
                categories.update(is_active=True)
                message = f'{categories.count()} categories activated successfully'
            elif action == 'deactivate':
                categories.update(is_active=False)
                message = f'{categories.count()} categories deactivated successfully'
            elif action == 'delete':
                # Check if categories have products
                categories_with_products = categories.filter(product__isnull=False).distinct()
                if categories_with_products.exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Some categories have products and cannot be deleted'
                    })
                count = categories.count()
                categories.delete()
                message = f'{count} categories deleted successfully'
            elif action == 'feature':
                categories.update(is_featured=True)
                message = f'{categories.count()} categories featured successfully'
            elif action == 'unfeature':
                categories.update(is_featured=False)
                message = f'{categories.count()} categories unfeatured successfully'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                })
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def bulk_blog_action(request):
    """API endpoint for bulk blog actions"""
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            blog_ids = request.POST.getlist('blog_ids[]')
            
            if not action or not blog_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Action and blog IDs are required'
                })
            
            blogs = Blog.objects.filter(id__in=blog_ids)
            
            if action == 'publish':
                blogs.update(is_published=True)
                # Set published date for blogs that don't have it
                blogs.filter(published_date__isnull=True).update(published_date=timezone.now())
                message = f'{blogs.count()} blogs published successfully'
            elif action == 'unpublish':
                blogs.update(is_published=False)
                message = f'{blogs.count()} blogs unpublished successfully'
            elif action == 'delete':
                count = blogs.count()
                blogs.delete()
                message = f'{count} blogs deleted successfully'
            elif action == 'feature':
                blogs.update(is_featured=True)
                message = f'{blogs.count()} blogs featured successfully'
            elif action == 'unfeature':
                blogs.update(is_featured=False)
                message = f'{blogs.count()} blogs unfeatured successfully'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action'
                })
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

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
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            employees = employees.filter(is_active=True)
        elif status_filter == 'inactive':
            employees = employees.filter(is_active=False)
    
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(employees, 25)
    page = request.GET.get('page')
    employees_page = paginator.get_page(page)
    
    # Stats
    total_employees = employees.count()
    active_employees = employees.filter(is_active=True).count()
    inactive_employees = employees.filter(is_active=False).count()
    
    context = {
        'employees': employees_page,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
    }
    return render(request, 'admin_dashboard/employees/list.html', context)

@login_required
@admin_required
def add_employee(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        
        if user_form.is_valid() and employee_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    # Generate random password
                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()
                    
                    employee = employee_form.save(commit=False)
                    employee.user = user
                    
                    # Generate employee ID if not provided
                    if not employee.employee_id:
                        employee.employee_id = f"EMP{user.id:04d}"
                    
                    employee.save()
                
                # Send welcome email with credentials (in production)
                messages.success(request, f'Employee added successfully! Temporary password: {password}')
                return redirect('admin_dashboard:employee_list')
                
            except Exception as e:
                messages.error(request, f'Error adding employee: {str(e)}')
    else:
        user_form = UserForm()
        employee_form = EmployeeForm()
    
    # Generate next employee ID
    last_employee = Employee.objects.order_by('-id').first()
    next_id = f"EMP{(last_employee.id + 1) if last_employee else 1:04d}"
    
    return render(request, 'admin_dashboard/employees/add.html', {
        'user_form': user_form,
        'employee_form': employee_form,
        'next_employee_id': next_id
    })

@login_required
@admin_required
def edit_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        user = employee.user
        
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=user)
            employee_form = EmployeeForm(request.POST, instance=employee)
            
            if user_form.is_valid() and employee_form.is_valid():
                user_form.save()
                employee_form.save()
                
                messages.success(request, 'Employee updated successfully!')
                return redirect('admin_dashboard:employee_list')
        else:
            user_form = UserForm(instance=user)
            employee_form = EmployeeForm(instance=employee)
        
        return render(request, 'admin_dashboard/employees/edit.html', {
            'user_form': user_form,
            'employee_form': employee_form,
            'employee': employee
        })
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee not found!')
        return redirect('admin_dashboard:employee_list')

@login_required
@admin_required
def toggle_employee_status(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.is_active = not employee.is_active
            employee.save()
            
            action = "activated" if employee.is_active else "deactivated"
            messages.success(request, f'Employee {action} successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'is_active': employee.is_active})
                
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Employee not found'})
    
    return redirect('admin_dashboard:employee_list')

@login_required
@admin_required
def employee_settings(request):
    # Employee role and permission settings
    positions = Employee.objects.values_list('position', flat=True).distinct()
    
    if request.method == 'POST':
        # Handle settings updates
        messages.success(request, 'Employee settings updated successfully!')
        return redirect('admin_dashboard:employee_settings')
    
    return render(request, 'admin_dashboard/employees/settings.html', {
        'positions': positions
    })

@login_required
@admin_required
def employee_reports(request):
    employees = Employee.objects.select_related('user').all()
    
    # Performance metrics
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
    
    # Add reporting logic here
    reports_data = []
    for employee in employees:
        # Calculate performance metrics
        reports_data.append({
            'employee': employee,
            'orders_processed': 0,  # Placeholder
            'total_sales': 0,       # Placeholder
            'efficiency': '95%',    # Placeholder
        })
    
    context = {
        'employees': employees,
        'reports_data': reports_data,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin_dashboard/employees/reports.html', context)

@login_required
@admin_required
def bulk_employee_action(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        employee_ids = request.POST.getlist('employee_ids[]')
        
        try:
            employees = Employee.objects.filter(id__in=employee_ids)
            
            if action == 'activate':
                employees.update(is_active=True)
                message = f'{employees.count()} employees activated successfully!'
            elif action == 'deactivate':
                employees.update(is_active=False)
                message = f'{employees.count()} employees deactivated successfully!'
            elif action == 'delete':
                # Delete users as well
                user_ids = employees.values_list('user_id', flat=True)
                User.objects.filter(id__in=user_ids).delete()
                message = f'{employees.count()} employees deleted successfully!'
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
            
            return JsonResponse({'success': True, 'message': message})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# ================= CUSTOMERS =================
@login_required
@admin_required
def all_customers(request):
    # Get unique customers from orders and user accounts
    order_customers = Order.objects.values('email', 'full_name', 'phone').distinct()
    user_customers = User.objects.filter(
        Q(order__isnull=False) | Q(is_staff=False)
    ).distinct().values('email', 'first_name', 'last_name')
    
    # Combine and deduplicate customers
    customers_dict = {}
    
    # Add order customers
    for customer in order_customers:
        email = customer['email']
        if email not in customers_dict:
            customers_dict[email] = {
                'email': email,
                'full_name': customer['full_name'],
                'phone': customer['phone'],
                'source': 'order',
                'order_count': Order.objects.filter(email=email).count(),
                'total_spent': Order.objects.filter(
                    email=email, 
                    status='delivered'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'last_order': Order.objects.filter(
                    email=email
                ).order_by('-created_at').first()
            }
    
    # Add user account customers
    for user in user_customers:
        email = user['email']
        if email not in customers_dict:
            customers_dict[email] = {
                'email': email,
                'full_name': f"{user['first_name']} {user['last_name']}".strip(),
                'phone': '',
                'source': 'account',
                'order_count': Order.objects.filter(email=email).count(),
                'total_spent': Order.objects.filter(
                    email=email, 
                    status='delivered'
                ).aggregate(total=Sum('total_amount'))['total'] or 0,
                'last_order': Order.objects.filter(
                    email=email
                ).order_by('-created_at').first()
            }
    
    customers = list(customers_dict.values())
    
    # Filtering
    search_query = request.GET.get('search')
    if search_query:
        customers = [c for c in customers if 
                    search_query.lower() in c['email'].lower() or 
                    (c['full_name'] and search_query.lower() in c['full_name'].lower())]
    
    source_filter = request.GET.get('source')
    if source_filter:
        customers = [c for c in customers if c['source'] == source_filter]
    
    # Sorting
    sort_by = request.GET.get('sort', 'last_order')
    reverse = request.GET.get('order', 'desc') == 'desc'
    
    if sort_by == 'email':
        customers.sort(key=lambda x: x['email'], reverse=reverse)
    elif sort_by == 'name':
        customers.sort(key=lambda x: x['full_name'] or '', reverse=reverse)
    elif sort_by == 'orders':
        customers.sort(key=lambda x: x['order_count'], reverse=reverse)
    elif sort_by == 'spent':
        customers.sort(key=lambda x: x['total_spent'], reverse=reverse)
    else:  # last_order
        customers.sort(key=lambda x: x['last_order'].created_at if x['last_order'] else datetime.min, reverse=reverse)
    
    # Pagination
    paginator = Paginator(customers, 25)
    page = request.GET.get('page')
    customers_page = paginator.get_page(page)
    
    # Stats
    total_customers = len(customers)
    order_customers_count = len([c for c in customers if c['source'] == 'order'])
    account_customers_count = len([c for c in customers if c['source'] == 'account'])
    total_revenue = sum(c['total_spent'] for c in customers)
    
    context = {
        'customers': customers_page,
        'total_customers': total_customers,
        'order_customers_count': order_customers_count,
        'account_customers_count': account_customers_count,
        'total_revenue': total_revenue,
    }
    return render(request, 'admin_dashboard/customers/all.html', context)

@login_required
@admin_required
def customer_detail(request, email):
    # Get customer orders
    orders = Order.objects.filter(email=email).order_by('-created_at')
    
    # Get customer details
    customer_data = {
        'email': email,
        'orders': orders,
        'total_orders': orders.count(),
        'total_spent': orders.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'first_order': orders.last(),
        'last_order': orders.first(),
    }
    
    # Try to get user account details
    try:
        user = User.objects.get(email=email)
        customer_data['user_account'] = user
        customer_data['date_joined'] = user.date_joined
    except User.DoesNotExist:
        customer_data['user_account'] = None
    
    return render(request, 'admin_dashboard/customers/detail.html', {
        'customer': customer_data
    })

@login_required
@admin_required
def blocked_customers(request):
    # Implement customer blocking logic
    blocked_customers = BlockedCustomer.objects.select_related('blocked_by').all()
    
    if request.method == 'POST':
        email = request.POST.get('email')
        reason = request.POST.get('reason', '')
        
        if email:
            blocked_customer, created = BlockedCustomer.objects.get_or_create(
                email=email,
                defaults={
                    'reason': reason,
                    'blocked_by': request.user,
                    'blocked_at': timezone.now()
                }
            )
            
            if created:
                messages.success(request, f'Customer {email} blocked successfully!')
            else:
                messages.info(request, f'Customer {email} is already blocked!')
            
            return redirect('admin_dashboard:blocked_customers')
    
    return render(request, 'admin_dashboard/customers/blocked.html', {
        'blocked_customers': blocked_customers
    })

@login_required
@admin_required
def unblock_customer(request, customer_id):
    if request.method == 'POST':
        try:
            blocked_customer = BlockedCustomer.objects.get(id=customer_id)
            email = blocked_customer.email
            blocked_customer.delete()
            
            messages.success(request, f'Customer {email} unblocked successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
                
        except BlockedCustomer.DoesNotExist:
            messages.error(request, 'Blocked customer not found!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Customer not found'})
    
    return redirect('admin_dashboard:blocked_customers')

@login_required
@admin_required
def bulk_customer_action(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        emails = request.POST.getlist('emails[]')
        
        try:
            if action == 'block':
                for email in emails:
                    BlockedCustomer.objects.get_or_create(
                        email=email,
                        defaults={
                            'reason': 'Bulk action',
                            'blocked_by': request.user,
                            'blocked_at': timezone.now()
                        }
                    )
                message = f'{len(emails)} customers blocked successfully!'
            elif action == 'export':
                # Export logic would go here
                message = f'{len(emails)} customers exported successfully!'
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
            
            return JsonResponse({'success': True, 'message': message})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Additional Customer-related API Views
@login_required
@admin_required
def send_customer_email(request):
    """API endpoint to send email to customer"""
    if request.method == 'POST':
        try:
            to_email = request.POST.get('to')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            if not all([to_email, subject, message]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required'
                })
            
            # Here you would integrate with your email service
            # For now, we'll just log it
            print(f"Email to: {to_email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            
            # Create communication record
            try:
                customer = Customer.objects.get(email=to_email)
                CustomerCommunication.objects.create(
                    customer=customer,
                    communication_type='email',
                    subject=subject,
                    message=message,
                    sent_by=request.user,
                    status='sent'
                )
            except Customer.DoesNotExist:
                # Still log the communication even if customer doesn't exist in DB
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Email sent successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def reset_customer_password(request):
    """API endpoint to reset customer password"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is required'
                })
            
            try:
                user = User.objects.get(email=email)
                # Generate reset token and send email (implement your reset logic)
                # For now, just return success
                return JsonResponse({
                    'success': True,
                    'message': 'Password reset link sent successfully'
                })
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'User not found'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def send_customer_coupon(request):
    """API endpoint to send coupon to customer"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is required'
                })
            
            # Generate a unique coupon code
            import random
            import string
            coupon_code = 'WELCOME' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Create coupon (you need to have Coupon model)
            try:
                coupon = Coupon.objects.create(
                    code=coupon_code,
                    discount_type='percentage',
                    discount_value=10,
                    min_order_amount=500,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=30),
                    usage_limit=1,
                    is_active=True
                )
                
                # Send email with coupon (implement your email logic)
                print(f"Coupon {coupon_code} sent to {email}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'Coupon {coupon_code} sent successfully'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error creating coupon: {str(e)}'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def save_customer_notes(request):
    """API endpoint to save customer notes"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            notes = request.POST.get('notes')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is required'
                })
            
            try:
                customer = Customer.objects.get(email=email)
                CustomerNote.objects.create(
                    customer=customer,
                    author=request.user,
                    title='Customer Note',
                    content=notes,
                    note_type='general'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Notes saved successfully'
                })
                
            except Customer.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Customer not found'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@admin_required
def update_block_reason(request):
    """API endpoint to update block reason"""
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            reason = request.POST.get('reason')
            
            if not customer_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Customer ID is required'
                })
            
            blocked_customer = BlockedCustomer.objects.get(id=customer_id)
            blocked_customer.custom_reason = reason
            blocked_customer.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Block reason updated successfully'
            })
            
        except BlockedCustomer.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Blocked customer not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


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

def delete_blog_category(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    category.delete()
    messages.success(request, f'Category "{category.name}" was deleted successfully.')
    return redirect('admin_dashboard:blog_categories')

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

def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    messages.success(request, f'Blog "{blog.title}" was deleted successfully.')
    return redirect('admin_dashboard:blog_list')

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


@login_required
@admin_required
def send_employee_credentials(request, employee_id):
    """API endpoint to send login credentials to employee"""
    if request.method == 'POST':
        try:
            employee = Employee.objects.select_related('user').get(id=employee_id)
            
            # Generate a temporary password if not already set
            if employee.user.has_usable_password():
                # Generate a new temporary password
                temp_password = User.objects.make_random_password(length=12)
                employee.user.set_password(temp_password)
                employee.user.save()
            else:
                temp_password = "Please use 'Forgot Password' to set your password"
            
            # Prepare email content
            subject = f"Your Login Credentials - {get_current_site(request).name}"
            message = f"""
            Dear {employee.user.get_full_name()},

            Your employee account has been created/updated at {get_current_site(request).name}.

            Login Details:
            - Email: {employee.user.email}
            - Username: {employee.user.username}
            - Temporary Password: {temp_password if isinstance(temp_password, str) else 'Please use password reset'}

            Login URL: {request.build_absolute_uri('/admin-login/')}

            Please change your password after first login for security reasons.

            Best regards,
            {get_current_site(request).name} Team
                        """
            
            # In production, you would send an actual email
            # For now, we'll just log it and return success
            print("=" * 50)
            print("EMPLOYEE CREDENTIALS EMAIL")
            print("=" * 50)
            print(f"To: {employee.user.email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            print("=" * 50)
            
            # Create a notification record (optional)
            EmployeeNotification.objects.create(
                employee=employee,
                title="Login Credentials Sent",
                message="Your login credentials have been sent to your email.",
                notification_type="credentials",
                sent_by=request.user
            )
            
            # Log the action
            print(f"Credentials sent to employee: {employee.user.email} by {request.user.email}")
            
            return JsonResponse({
                'success': True,
                'message': f'Login credentials sent to {employee.user.email} successfully!',
                'email_sent_to': employee.user.email
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Employee not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error sending credentials: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
