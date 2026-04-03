from django.contrib import admin
from .models import ShippingAddress,Order,OrderItems
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItems)

#Lets create an order item inline
class OrderItemInline(admin.StackedInline):
    model = OrderItems
    extra = 0

#extend our order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ['date_ordered']
    fields = ['user','full_name','email','shipping_address','amount_paid','date_ordered','shipped','date_shipped']
    inlines = [OrderItemInline]

#unregister order model
admin.site.unregister(Order)

#Re-register our order and orderadmin
admin.site.register(Order,OrderAdmin)
