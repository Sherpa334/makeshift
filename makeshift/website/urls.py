from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="loginPage"),
    path("register/", views.registerPage, name="registerPage"),
    path("static", views.staticPage, name="staticPage")
]