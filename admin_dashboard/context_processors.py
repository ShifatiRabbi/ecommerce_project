from .models import SiteSetting

def admin_settings(request):
    """
    Add admin-related settings to all admin templates
    """
    settings = SiteSetting.objects.first()
    if not settings:
        settings = SiteSetting.objects.create()
    
    return {
        'admin_settings': settings,
        'admin_site_name': settings.site_name if settings else 'Admin Dashboard'
    }