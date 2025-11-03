from .models import DefaultSiteSetting

def admin_settings(request):
    """
    Add admin-related settings to all admin templates
    """
    settings = DefaultSiteSetting.objects.first()
    if not settings:
        settings = DefaultSiteSetting.objects.create()
    
    return {
        'admin_settings': settings,
        'admin_site_name': settings.site_name if settings else 'Admin Dashboard'
    }