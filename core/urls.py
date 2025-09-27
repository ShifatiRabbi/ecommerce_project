from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('return-refund/', views.return_refund, name='return_refund'),
    path('change-language/', views.change_language, name='change_language'),
]