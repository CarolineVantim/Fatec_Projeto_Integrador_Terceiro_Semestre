from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("register", views.register, name="registration"),
    path("login_user", views.login_user, name="login_user"),
    path("logout_user", views.logout_user, name="logout_user"),
    path("home", views.home, name="home"),
    path('product/<str:pk>', views.productdetail, name='productdetail'),
    path('delete_item/<int:user_id>/<str:reference>', views.delete_item, name='delete_item'),
    path('donation_list/<str:user_id>', views.index_donations, name='donation_list'),
    path('add_product/<int:user_id>/<str:reference>/<str:quantaty>', views.add_product_list, name='add_product_list'),
    path('donate_product/<int:pk>/<int:user_id>', views.donate_product, name='donate_product'),
    path("list_institution", views.list_institution, name="list_institution"),
    path('about_product/<str:reference>', views.know_about_product, name='know_about_product'),
    path('close_list/<int:user_id>/<int:list_control_id>', views.close_list, name='close_list'),
    path('specific_list/<int:list_control_id>/<int:user_id>', views.specific_list, name='specific_list'),
    path('learn_more', views.learn_more, name='learn_more')
]

urlpatterns += staticfiles_urlpatterns()
