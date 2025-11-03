from core.models import SiteSettings
from admin_dashboard.models import DefaultSiteSetting
from shop.models import Category
from cart.cart import Cart

def site_settings(request):
    # Use DefaultSiteSetting for basic settings
    default_settings = DefaultSiteSetting.get_default_settings()
    
    # Use SiteSettings for header/footer templates (from your existing code)
    settings = SiteSettings.get_settings()
    
    # Determine which header and footer to use
    header_template = f'includes/headers/{settings.active_header}.html'
    footer_template = f'includes/footers/{settings.active_footer}.html'
    
    # Get categories for menus
    categories = Category.objects.filter(is_active=True, parent__isnull=True)[:8]
    
    # Get cart count
    cart = Cart(request)
    
    return {
        'site_settings': settings,  # For header/footer templates
        'default_settings': default_settings,  # For basic site info
        'header_template': header_template,
        'footer_template': footer_template,
        'categories': categories,
        'cart': cart,
    }