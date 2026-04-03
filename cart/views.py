from django.shortcuts import render, get_object_or_404
from .cart import Cart
from shopping.models import product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.


def cart_summary(request):
    #Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities= cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals})


def cart_add(request):
    cart = Cart(request)
    if request.method == 'POST':
        items_id = request.POST.get('items_id')
        items_qty = request.POST.get('items_qty')
        products = get_object_or_404(product,id=items_id)
        cart = request.session.get('cart',{})
        cart[items_id]= cart.get(items_id,0) + 1
        #cart.add(product=product, quantity=items_qty)
        request.session['cart']= cart
        request.session.modified = True
        #Get cart quantity
        cart_quantity= cart.__len__()
        messages.success(request,("product added to Cart..."))

        return JsonResponse({'qty':cart_quantity,'products_id':products.id})
    return JsonResponse({'error':'invalid request'}, status=400)
    
    

def cart_delete(request):

    cart = Cart(request)
    if request.POST.get('action') == 'post':
        items_id = int(request.POST.get('items_id'))
        # call delete function in cart
        cart.delete(items=items_id)

        response = JsonResponse({'items':items_id})
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        items_id = int(request.POST.get('items_id'))
        items_qty = int(request.POST.get('items_qty'))
        cart.update(items=items_id,quantity=items_qty)

        response = JsonResponse({'qty':items_qty})
        return response