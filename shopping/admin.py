from django.contrib import admin
from .models import category,customer,product,order,profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

# Register your models here.

admin.site.register(category)
admin.site.register(customer)
admin.site.register(product)
admin.site.register(order)
admin.site.register(profile)


#Mix profile info and user info
class ProfileInLine(admin.StackedInline):
    model = profile
    can_delete = False

#extend the user model
class UserAdmin(DefaultUserAdmin):
    inlines = [ProfileInLine]
   

# Re-register the new way
admin.site.unregister(User)
admin.site.register(User,UserAdmin)


