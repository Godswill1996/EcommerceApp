from django.urls import path

from . import views

urlpatterns = [path("", views.ecommerce, name="ecommerce"),
               path('about/', views.about, name='about'),
               path('login/',views.login_user, name='login'),
               path('logout/',views.logout_user,name='logout'),
               path('register/',views.register_user, name='register'),
               path('update_password/',views.update_password, name='update_password'),
               path('update_info/',views.update_info, name='update_info'),
               path('update_user/',views.update_user, name='update_user'),
               path('pro/<int:pk>',views.pro, name='pro'),
               path('cat/<str:foo>',views.cat, name='cat'),
               path('search/',views.search, name='search'),


               ]