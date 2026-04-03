from django.shortcuts import render,redirect
from .models import product,category,profile
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUser, ChangePasswordForm,UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q


# Create your views here.

def search(request):
     #Deterine if they filled out the form
     if request.method == 'POST':
          searched = request.POST['searched']
          # Query the products DB Model
          searched = product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
          #Test for null
          if not searched:
               messages.success(request, "That product doest not exist")
               return render(request, 'search.html', {})
          else:
               return render(request, 'search.html', {'searched':searched})

     else:
          return render(request, 'search.html', {})
     



def update_info(request):
     if request.user.is_authenticated:
          #Get current user
          current_user = profile.objects.get(user__id=request.user.id)
          #Get current user's shipping info
          shipping_user = ShippingAddress.objects.get(user=request.user)
          #Get original user form
          form = UserInfoForm(request.POST or None, instance = current_user)
          #Get user's shipping form
          shipping_form = ShippingForm(request.POST or None, instance = shipping_user)

          if form.is_valid() or shipping_form.is_valid():
               #save original form
               form.save()
               #save shipping form
               shipping_form.save()
               messages.success(request, "Your info has been updated")
               return redirect('ecommerce')
          return render(request,'update_info.html',{'form':form, 'shipping_form':shipping_form})
     else:
          messages.success(request, "You must be logged in to access this page")
          return redirect('ecommerce')




def update_password(request):
     if request.user.is_authenticated:
          current_user = request.user
          #Did they fill out the form
          if request.method == 'POST':
               form = ChangePasswordForm(current_user,request.POST)
               #Check if form is valid
               if form.is_valid():
                    form.save()
                    messages.success(request, "Your password has been updated,please login again...")
                    #login(request, current_user)
                    return redirect('login')
               else:
                    for error in list(form.errors.values()):
                         messages.error(request, error)
                         return redirect('update_password')

              
          else:
               form = ChangePasswordForm(current_user)
               return render(request, 'update_password.html', {'form':form})
          
     else:
          messages.success(request, "You must be logged in to access this page")
          return redirect('ecommerce')




def update_user(request):

     if request.user.is_authenticated:
          current_user = User.objects.get(id=request.user.id)
          user_form = UpdateUser(request.POST or None, instance = current_user)

          if user_form.is_valid():
               user_form.save()

               login(request, current_user)
               messages.success(request, "User has been updated")
               return redirect('ecommerce')
          return render(request,'update_user.html',{'user_form':user_form})
     else:
          messages.success(request, "You must be logged in to access this page")
          return redirect('ecommerce')


def cat(request, foo):
     # replace hyphens with spaces
     foo = foo.replace('-', ' ')
     # grab the category from the url

     try:
          #look up the category
          categories=category.objects.get(name=foo) 
          goods= product.objects.filter(categories=category)
          return render(request, 'cat.html', {'goods':goods, 'categories':categories})
          
     

     except:
          messages.success(request,("That category doesn't exit"))
          return redirect('ecommerce')


def pro(request,pk):
     items = product.objects.get(id=pk)

     return render(request, 'pro.html',{'items':items})



def ecommerce(request):
     products = product.objects.all()
     
     
     return render(request, "ecommerce.html",{'products':products})

def about(request):
     return render(request, "about.html",{})

def login_user(request):
     if request.method =='POST' :
         username = request.POST['username']
         password = request.POST['password']
         user = authenticate(request, username=username,password=password)
         if user is not None:
              login(request,user)
              messages.success(request,("You have been logged in"))
              return redirect('ecommerce')
         else:
              messages.success(request,("There was an error,please check details"))
              return redirect('login')
              
         
     else:
          return render(request, 'login.html', {})
     
     
     

def logout_user(request):
     logout(request)
     messages.success(request,("You have been logged out..."))
     return redirect('ecommerce')



def register_user(request):
     form = SignUpForm()
     if request.method == "POST":
          form = SignUpForm(request.POST)
          if form.is_valid():
               form.save()
               username = form.cleaned_data['username']
               password = form.cleaned_data['password1']
               #log in user
               user = authenticate(username = username, password = password)
               login(request, user)
               messages.success(request,("You have register successfully...."))
               return redirect('update_info')
          else:
               messages.success(request,("oops there was a problem registering,please try again..."))
               return redirect('register')
               
          
     else:
          return render(request, 'register.html', {'form':form})
    
     