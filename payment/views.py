from django.shortcuts import render,redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItems
from django.contrib import messages
from django.contrib.auth.models import User
from shopping.models import product,profile
import datetime
import os
import requests

# Create your views here.

def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # Get the order
        order = Order.objects.get(id=pk)
        #Get order items
        items = OrderItems.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            # check if true or false
            if status == 'true':
                #Get the order
                order = Order.objects.filter(id=pk)
                #Update status
                now = datetime.datetime.now()
                order.update(shipped = True,date_shipped = now )
            else:
                #Get the order
                order = Order.objects.filter(id=pk)
                #Update status
                order.update(shipped = False)
            messages.success(request,'Shipping Status Updated')
            return redirect('ecommerce')


        return render(request, 'payment/orders.html', {"order":order, "items":items})
    
    else:
        messages.success(request,'Access Denied')
        return redirect('ecommerce')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #Get the order
            order = Order.objects.filter(id=num)
            #Grab datetime
            now = datetime.datetime.now()
            #Update order
            orders.update(shipped = True,date_shipped = now )
            #Redirect
            messages.success(request,'Shipping Status Updated')
            return redirect('ecommerce')

        return render(request, 'payment/not_shipped_dash.html', {'orders':orders})
    
    else:
        messages.success(request,'Access Denied')
        return redirect('ecommerce')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #Grab the order
            order = Order.objects.filter(id=num)
            #Grab datetime
            now = datetime.datetime.now()
            #Update order
            orders.update(shipped = False)
            #Redirect
            messages.success(request,'Shipping Status Updated')
            return redirect('ecommerce')
        

        return render(request, 'payment/shipped_dash.html', {'orders':orders})
    
    else:
        messages.success(request,'Access Denied')
        return redirect('ecommerce')

def process_order(request):
    if request.POST:
        #Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities= cart.get_quants
        totals = cart.cart_total()

        #Get billing info from the last page
        payment_form = PaymentForm(request.POST or None)
        #Get shipping session data
        my_shipping = request.session.get('my_shipping')

        #Gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        
        #print(my_shipping)
        #Create shipping address from shipping info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        #Paystack Details
        url= 'https://api.paystack.co/transaction/initialize'
        headers = {'Authorization': f'Bearer {os.environ.get("PAYSTACK_SECRET_KEY")}','Content-Type':'application/json',}
        data = {'email':email, 'amount': str(int(totals * 100)),
                'callback_url': 'https://ecommerceapp-production-735f.up.railway.app/payment/process_order_verify',}
        
        response = requests.post(url, headers=headers, json=data)
        res_data = response.json()
        if res_data['status']:
            return redirect(res_data['data']['authorization_url'])
        
        return redirect('checkout')
        


        #Create an order
        
        if request.user.is_authenticated:
            #logged in
            user = request.user
            # create other
            create_order = Order(user=user , full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            #Add order items
            #Get the order Id
            order_id = create_order.pk
            #Get items info
            for items in cart_products:
                #Get items ID
                items_id = items.id
                #Get items price
                if items.is_sale:
                    price = items.sale_price
                else:
                    price = items.price
                #Get Quantity
                for key,value in quantities().items():
                    if int(key) == items.id :
                        #Create order item
                        create_order_item = OrderItems(order_id=order_id, products_id=items_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            #Delete our cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    #Delete the key
                    del request.session[key]

            # Delete Cart from Database (old_cart field)
            current_user = profile.objects.filter(user__id=request.user.id )
            #Delete shopping cart in database (old_cart field)
            current_user.update(old_cart="")




            messages.success(request,'Order placed')
            return redirect('ecommerce')
         

        else:
            #not logged in
            # create other
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            #Add order items
            #Get the order Id
            order_id = create_order.pk
            #Get items info
            for items in cart_products:
                #Get items ID
                items_id = items.id
                #Get items price
                if items.is_sale:
                    price = items.sale_price
                else:
                    price = items.price
                #Get Quantity
                for key,value in quantities().items():
                    if int(key) == items.id :
                        #Create order item
                        create_order_item = OrderItems(order_id=order_id, products_id=items_id, quantity=value, price=price)
                        create_order_item.save() 

            #Delete our cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    #Delete the key
                    del request.session[key]



            messages.success(request,'Order placed')
            return redirect('ecommerce')
 

    else:
        messages.success(request,'Access Denied')
        return redirect('ecommerce')

def process_order_verify(request):
    reference = request.GET.get('reference')
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    headers = {'Authorization': f'Bearer {os.environ.get("PAYSTACK_SECRET_KEY")}',}
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == 'success':
            cart = Cart(request)
            cart_products = cart.get_prods()
            quantities = cart.get_quants
            totals = cart.cart_total()
            shipping_data= request.session.get('my_shipping',{})
            full_name = shipping_data.get('shipping_full_name','Guest')
            email = shipping_data.get('shipping_email',res_data['data']['customer']['email'])
            address = f"{shipping_data.get('shipping_address1')}, {shipping_data.get('shipping_city')}"
            


            new_order = Order.objects.create(user=request.user if request.user.is_authenticated else None,full_name=full_name ,email=email,amount_paid=totals,shipping_address=address)
            for item in cart_products:
                product_id = str(item.id)
                OrderItems.objects.create(order=new_order,products=item,user=request.user if request.user.is_authenticated else None,quantity=quantities.get(product_id,1),price=item.price if not item.is_sale else item.sale_price)
            
            request.session.pop('cart',None)
            request.session.modified = True

            return render(request,'payment/payment_success.html',{'order':new_order})
    else:
        return render(request,'payment/payment_failed.html')



def billing_info(request):
    if request.POST:


        #Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities= cart.get_quants
        totals = cart.cart_total()

        #create a session with Shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping


        #check to see if user is logged in
        if request.user.is_authenticated:
            # Get the billing form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_info':request.POST, 'billing_form':billing_form})
        else:
            #not logged in
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_info':request.POST,'billing_form':billing_form})

        shipping_form = request.POST


        return render(request, 'payment/billing_info.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_form':shipping_form})
    else:
        messages.success(request,'Access Denied')
        return redirect('ecommerce')




def checkout(request):
    #Get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities= cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        #Check out as User
        #Shipping user
        shipping_user = ShippingAddress.objects.filter(user=request.user).first()
        #Shipping form
        shipping_form = ShippingForm(request.POST or None, instance = shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals, 'shipping_form':shipping_form })
    else:
        #Check out as guest
        shipping_form = ShippingForm(request.POST or None,)
        return render(request, 'payment/checkout.html', {'cart_products':cart_products,'quantities':quantities,'totals':totals,'shipping_form':shipping_form})


def payment_success(request):
    
    return render(request,'payment/payment_success.html',{}) 

def payment_failed(request):
    
    return render(request,'payment/payment_failed.html',{}) 