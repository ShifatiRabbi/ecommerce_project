from core.models import SiteSettings

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
    except:
        settings = SiteSettings.objects.create()
    
    # Determine which header to use
    header_template = f'includes/headers/{settings.active_header}.html'
    
    return {
        'site_settings': settings,
        'header_template': header_template
    }