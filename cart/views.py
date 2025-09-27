from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from shop.models import Product
from .cart import Cart
from .models import Order, OrderItem
import random
import string

def cart_detail(request):
    return render(request, 'cart/cart.html')

def cart_add(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = Cart(request)
        cart.add(product, quantity)
        
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart),
            'message': 'Product added to cart!'
        })
    return JsonResponse({'success': False})

def cart_remove(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product)
        
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart),
            'message': 'Product removed from cart!'
        })
    return JsonResponse({'success': False})

def cart_update(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = Cart(request)
        cart.add(product, quantity, override_quantity=True)
        
        cart_item = None
        for item in cart:
            if str(item['product'].id) == product_id:
                cart_item = item
                break
        
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart),
            'item_total': float(cart_item['total_price']) if cart_item else 0,
            'cart_total': float(cart.get_total_price())
        })
    return JsonResponse({'success': False})

def checkout(request):
    cart = Cart(request)
    if not cart:
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        # Generate order number
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        order = Order.objects.create(
            order_number=order_number,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            postal_code=request.POST.get('postal_code'),
            total_amount=cart.get_total_price()
        )
        
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        cart.clear()
        return render(request, 'cart/checkout_success.html', {'order': order})
    
    return render(request, 'cart/checkout.html')