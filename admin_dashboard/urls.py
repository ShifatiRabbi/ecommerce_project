from django.urls import path
from admin_dashboard import views

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
    path('payment/sslcommerz/', views.sslcommerz_settings, name='ssl_commerz'),
    path('payment/bkash/', views.bkash_settings, name='bkash_online'),
    path('payment/manual/', views.manual_payment_settings, name='manual_payment'),
    
    # Employee URLs
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/list/', views.employee_list, name='employee_list'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('employees/settings/', views.employee_settings, name='employee_settings'),
    path('employees/reports/', views.employee_reports, name='employee_reports'),
    path('employees/toggle-status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('employees/bulk-action/', views.bulk_employee_action, name='bulk_employee_action'),
    # path('employees/send-credentials/<int:employee_id>/', views.send_employee_credentials, name='send_employee_credentials'),

    # Customer URLs
    path('customers/all/', views.all_customers, name='all_customers'),
    path('customers/blocked/', views.blocked_customers, name='blocked_customers'),
    path('customers/detail/<str:email>/', views.customer_detail, name='customer_detail'),
    path('customers/unblock/<int:customer_id>/', views.unblock_customer, name='unblock_customer'),
    path('customers/bulk-action/', views.bulk_customer_action, name='bulk_customer_action'),
    path('customers/send-email/', views.send_customer_email, name='send_customer_email'),
    path('customers/reset-password/', views.reset_customer_password, name='reset_customer_password'),
    path('customers/send-coupon/', views.send_customer_coupon, name='send_customer_coupon'),
    path('customers/save-notes/', views.save_customer_notes, name='save_customer_notes'),
    path('customers/update-block-reason/', views.update_block_reason, name='update_block_reason'),
    
    # Blogs
    path('blogs/categories/', views.blog_categories, name='all_blog_categories'),
    path('blogs/categories/add/', views.add_blog_category, name='add_blog_category'),
    path('blogs/categories/delete/<int:pk>/', views.delete_blog_category, name='delete_blog_category'),
    path('blogs/add/', views.add_blog, name='add_blog'),
    path('blogs/list/', views.blog_list, name='all_blogs'),
    path('blogs/delete/<int:pk>/', views.delete_blog, name='delete_blog'),
    
    # Marketing
    path('marketing/facebook/conversion-api/', views.facebook_conversion_api, name='facebook_conversion_api'),
    path('marketing/facebook/messenger/', views.facebook_messenger, name='messenger_integration'),
    path('marketing/google/gtm/', views.google_gtm, name='google_tag_manager'),
    path('marketing/google/ga4/', views.google_ga4, name='google_analytics'),
    path('marketing/seo/technical/', views.technical_seo, name='technical_seo'),
    path('marketing/seo/onpage/', views.onpage_seo, name='one_page_seo'),
    path('marketing/sms/api/', views.sms_api, name='sms_api'),
    path('marketing/sms/message/', views.sms_message, name='sms_message_writing'),
    path('marketing/live-chat/', views.live_chat, name='live_chat'),
    path('marketing/integrations/', views.third_party_integrations, name='third_party_integration'),
    
    # Manage Site
    path('manage/basic-settings/', views.basic_settings, name='basic_settings'),
    path('manage/homepage-design/', views.homepage_design, name='home_page_design'),
    path('manage/header-design/', views.header_design, name='header_design'),
    path('manage/footer-design/', views.footer_design, name='footer_design'),
    path('manage/product-page-design/', views.product_page_design, name='product_page_design'),
    path('manage/order-tracking/', views.order_tracking, name='order_tracking'),
    path('manage/checkout-design/', views.checkout_design, name='checkout_page_design'),
    path('manage/thankyou-design/', views.thankyou_design, name='thank_you_page'),
    path('manage/invoice-design/', views.invoice_design, name='invoice_design'),
    path('manage/custom-css/', views.custom_css, name='custom_css'),
    path('manage/custom-js/', views.custom_js, name='custom_js'),
    path('manage/banners/', views.banner_list, name='all_banners'),
    path('manage/banners/add/', views.add_banner, name='add_banner'),
    
    # Backend Customization
    path('customization/orders/', views.orders_customize, name='orders_customize'),
    path('customization/order-status/', views.order_status_customize, name='order_status_customize'),
    
    # Page Builder
    path('page-builder/create/', views.create_page, name='create_page'),
    path('page-builder/pages/', views.page_list, name='page_list'),
    path('page-builder/landing/create/', views.create_landing_page, name='landing_page'),
    path('page-builder/landing/list/', views.landing_page_list, name='landing_page_list'),
    path('page-builder/templates/', views.template_demo, name='template_demo'),
    
    # Profile
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('profile/logout/', views.admin_logout, name='admin_logout'),
    
    # AJAX endpoints
    path('ajax/upload-image/', views.ajax_upload_image, name='ajax_upload_image'),
    path('ajax/set-active-header/', views.ajax_set_active_header, name='ajax_set_active_header'),
    path('ajax/set-active-footer/', views.ajax_set_active_footer, name='ajax_set_active_footer'),
    path('ajax/save-header-settings/', views.ajax_save_header_settings, name='ajax_save_header_settings'),
    path('ajax/preview-header/', views.ajax_preview_header, name='ajax_preview_header'),
    path('ajax/update-order-status/', views.update_order_status, name='update_order_status'),
    path('ajax/update-inventory/', views.update_inventory, name='update_inventory'),
    path('ajax/get-order-stats/', views.get_order_stats, name='get_order_stats'),
    path('ajax/get-sales-data/', views.get_sales_data, name='get_sales_data'),

    # Additional API endpoints for AJAX
    path('api/category-stats/', views.category_stats, name='category_stats'),
    path('api/brand-stats/', views.brand_stats, name='brand_stats'),
    path('api/supplier-stats/', views.supplier_stats, name='supplier_stats'),
    path('api/recent-brands/', views.recent_brands, name='recent_brands'),
    path('api/toggle-blog-category/', views.toggle_blog_category, name='toggle_blog_category'),
    path('api/toggle-blog-status/', views.toggle_blog_status, name='toggle_blog_status'),
    path('api/bulk-category-action/', views.bulk_category_action, name='bulk_category_action'),
    path('api/bulk-blog-action/', views.bulk_blog_action, name='bulk_blog_action'),
]