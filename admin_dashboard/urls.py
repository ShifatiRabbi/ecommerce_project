from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Orders
    path('orders/completed/', views.completed_orders, name='completed_orders'),
    path('orders/incomplete/', views.incomplete_orders, name='incomplete_orders'),
    path('orders/fake/', views.fake_orders, name='fake_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Products
    path('products/add/', views.add_product, name='add_product'),
    path('products/list/', views.product_list, name='product_list'),
    path('products/reporting/', views.product_reporting, name='product_reporting'),
    path('products/categories/', views.category_list, name='category_list'),
    path('products/categories/add/', views.add_category, name='add_category'),
    path('products/brands/', views.brand_list, name='brand_list'),
    path('products/brands/add/', views.add_brand, name='add_brand'),
    path('products/suppliers/', views.supplier_list, name='supplier_list'),
    path('products/suppliers/add/', views.add_supplier, name='add_supplier'),
    path('products/inventory/', views.inventory_list, name='inventory_list'),
    
    # Offers
    path('offers/combo/add/', views.add_combo_offer, name='add_combo_offer'),
    path('offers/combo/list/', views.combo_offer_list, name='combo_offer_list'),
    path('offers/flash-sale/add/', views.add_flash_sale, name='add_flash_sale'),
    path('offers/flash-sale/list/', views.flash_sale_list, name='flash_sale_list'),
    path('offers/coupons/', views.coupon_list, name='coupon_list'),
    path('offers/discounts/', views.discount_settings, name='discount_settings'),
    path('offers/popup/', views.popup_offers, name='popup_offers'),
    
    # Courier & Delivery
    path('courier/charges/', views.courier_charges, name='courier_charges'),
    path('courier/api/', views.courier_api, name='courier_api'),
    
    # Payment
    path('payment/sslcommerz/', views.sslcommerz_settings, name='sslcommerz_settings'),
    path('payment/bkash/', views.bkash_settings, name='bkash_settings'),
    path('payment/manual/', views.manual_payment_settings, name='manual_payment_settings'),
    
    # Employees
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/list/', views.employee_list, name='employee_list'),
    path('employees/settings/', views.employee_settings, name='employee_settings'),
    path('employees/reports/', views.employee_reports, name='employee_reports'),
    
    # Customers
    path('customers/all/', views.all_customers, name='all_customers'),
    path('customers/blocked/', views.blocked_customers, name='blocked_customers'),
    
    # Blogs
    path('blogs/categories/', views.blog_categories, name='blog_categories'),
    path('blogs/categories/add/', views.add_blog_category, name='add_blog_category'),
    path('blogs/add/', views.add_blog, name='add_blog'),
    path('blogs/list/', views.blog_list, name='blog_list'),
    
    # Marketing
    path('marketing/facebook/conversion-api/', views.facebook_conversion_api, name='facebook_conversion_api'),
    path('marketing/facebook/messenger/', views.facebook_messenger, name='facebook_messenger'),
    path('marketing/google/gtm/', views.google_gtm, name='google_gtm'),
    path('marketing/google/ga4/', views.google_ga4, name='google_ga4'),
    path('marketing/seo/technical/', views.technical_seo, name='technical_seo'),
    path('marketing/seo/onpage/', views.onpage_seo, name='onpage_seo'),
    path('marketing/sms/api/', views.sms_api, name='sms_api'),
    path('marketing/sms/message/', views.sms_message, name='sms_message'),
    path('marketing/live-chat/', views.live_chat, name='live_chat'),
    path('marketing/integrations/', views.third_party_integrations, name='third_party_integrations'),
    
    # Manage Site
    path('manage/basic-settings/', views.basic_settings, name='basic_settings'),
    path('manage/homepage-design/', views.homepage_design, name='homepage_design'),
    path('manage/header-design/', views.header_design, name='header_design'),
    path('manage/footer-design/', views.footer_design, name='footer_design'),
    path('manage/product-page-design/', views.product_page_design, name='product_page_design'),
    path('manage/order-tracking/', views.order_tracking, name='order_tracking'),
    path('manage/checkout-design/', views.checkout_design, name='checkout_design'),
    path('manage/thankyou-design/', views.thankyou_design, name='thankyou_design'),
    path('manage/invoice-design/', views.invoice_design, name='invoice_design'),
    path('manage/custom-css/', views.custom_css, name='custom_css'),
    path('manage/custom-js/', views.custom_js, name='custom_js'),
    path('manage/banners/', views.banner_list, name='banner_list'),
    path('manage/banners/add/', views.add_banner, name='add_banner'),
    
    # Backend Customization
    path('customization/orders/', views.orders_customize, name='orders_customize'),
    path('customization/order-status/', views.order_status_customize, name='order_status_customize'),
    
    # Page Builder
    path('page-builder/create/', views.create_page, name='create_page'),
    path('page-builder/pages/', views.page_list, name='page_list'),
    path('page-builder/landing/create/', views.create_landing_page, name='create_landing_page'),
    path('page-builder/landing/list/', views.landing_page_list, name='landing_page_list'),
    path('page-builder/templates/', views.template_demo, name='template_demo'),
    
    # Profile
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/logout/', views.admin_logout, name='admin_logout'),
    
    # AJAX endpoints
    path('ajax/update-order-status/', views.update_order_status, name='update_order_status'),
    path('ajax/update-inventory/', views.update_inventory, name='update_inventory'),
    path('ajax/get-order-stats/', views.get_order_stats, name='get_order_stats'),
    path('ajax/get-sales-data/', views.get_sales_data, name='get_sales_data'),
]