from .cart import Cart
# create context processor so our cart can work on all pages

def cart(request):
    # return the default data from our cart
    return {'cart':Cart(request)}

def cart_count(request):
    cart = request.session.get("cart",{})
    count = sum(cart.values())
    return {"cart_count": count}