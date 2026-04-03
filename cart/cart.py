import json
from shopping.models import product, profile

class Cart():
    def __init__(self,request):
        self.session = request.session
        #Get request
        self.request = request
        
        self.cart = self.session.get('cart',{})

    def get_prods(self):
        #Get ids from cart
        product_ids = self.cart.keys()
        #Use ids to look up product in database
        products = product.objects.filter(id__in=product_ids)
        #Return those looked up product
        return products
    

    def add(self,product,quantity=1):
        items_id = str(product.id)
        items_qty= int(quantity)
        # Logic
        if items_id not in self.cart:
            
        
            self.cart[items_id] = {'price':str(product.price),'quantity':str(items_qty),}
            #self.cart[items_id] = int(items_qty)
        self.session.modified = True

        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = profile.objects.get(user=self.request.user)
            # Convert to json
            #carty = str(self.cart)
            #carty = carty.replace("\'","\"")
            #Save carty to profile model
            #current_user.update(old_cart=str(carty))
            current_user.old_cart = json.dumps(self.cart)
            current_user.save()
        


    def cart_total(self):
        #Get items IDS
        product_ids = self.cart.keys()
        #lookup those keys in our items database
        products = product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        #Start counting at 0
        total = 0
        for key, value in quantities.items():
            #convert key string into int so we can do the maths
            key = int(key)
            for prod in products:
                if prod.id == key:
                    if prod.is_sale:
                        total = total + (prod.sale_price * value)
                    else:
                        total = total + (prod.price * value)
                    
        return total
    def __len__(self):
        return len(self.cart)
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    

    def update(self,items,quantity):
        items_id = str(items)
        items_qty = int(quantity)
        # Get cart
        ourcart = self.cart
        #update dictionary/cart
        ourcart[items_id] = items_qty

        self.session.modified = True
        thing = self.cart
        return thing
    
    def delete(self,items):
        items_id = str(items)
        #Delete from dictionary/cart
        if items_id in self.cart:
            del self.cart[items_id]

        self.session.modified = True
    
    