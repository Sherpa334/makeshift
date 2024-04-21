from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.loginPage, name="loginPage"),
    path("login/", views.loginPage, name="loginPage"),
    path("register/", views.registerPage, name="registerPage"),
    path("static", views.staticPage, name="staticPage"),
    path("logout/", views.logoutRequest, name="logout"),
    path("home/", views.homePage, name="homePage"),
    path("next-profile/", views.nextProfile, name="nextProfile"),
    path('like-profile/', views.likeProfile, name='likeProfile'),
    path('chat/', views.chat)
]