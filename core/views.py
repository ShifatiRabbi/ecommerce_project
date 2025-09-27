from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.translation import get_language, activate
from core.models import ContactMessage, SiteSettings
from shop.models import Category, Product
import json

def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'core/home.html', context)

def contact(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            ContactMessage.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                subject=data.get('subject'),
                message=data.get('message')
            )
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error sending message.'})
    
    return render(request, 'core/contact.html')

def terms_conditions(request):
    return render(request, 'core/terms_conditions.html')

def return_refund(request):
    return render(request, 'core/return_refund.html')

def change_language(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        lang = request.POST.get('language', 'en')
        if lang in ['en', 'bn']:
            request.session['django_language'] = lang
            activate(lang)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})