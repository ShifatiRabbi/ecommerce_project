from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.shop, name='shop'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.product_search, name='product_search'),
]