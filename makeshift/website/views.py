from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.contrib import messages
import re

# Create your views here.
def loginPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, "static.html", context)
        else:
            messages.error(request, "Bad Credentials")
    return render(request, "loginPage.html", context)
    
def registerPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist")
            return render(request, "registerPage.html", context)

        if password != confirm_password:
            messages.error(request, "Passwords didn't match")
            return render(request, "registerPage.html", context)
        
        if len(password) < 8:
            messages.error(request, "Password too short")
            return render(request, "registerPage.html", context)
        
        # The password contains at least 1 lowercase letter
        if not re.search("[a-z]", password):
            messages.error(request, "Password did not contain at least 1 lowercase letter")
            return render(request, "registerPage.html", context)
        
        # The password contains at least 1 uppercase letter
        if not re.search("[A-Z]", password):
            messages.error(request, "Password did not contain at least 1 uppercase letter")
            return render(request, "registerPage.html", context)

        # The password contains at least 1 number
        if not re.search("[0-9]", password):
            messages.error(request, "Password did not contain at least 1 number")
            return render(request, "registerPage.html", context)

        if not re.search('[!@#$%^&()\-_=]', password):
            messages.error(request, "Password contains invalid special characters")
            return render(request, "registerPage.html", context)
        
        # The password does not contain any invalid characters (eg. any character that is not an alphanumeric or one of the 12 special characters)
        if not re.match("^[a-zA-Z0-9!@#$%^&()\-_=]+$", password):
            messages.error(request, "Passwords contained invalid characters")
            return render(request, "registerPage.html", context)
        
        user = User.objects.create_user(username, None, password)
        
        user.save()
        messages.success(request, "Account creation is successful")
        return redirect('loginPage')
    
    return render(request, "registerPage.html", context)

def staticPage(request):
    return render(request, "staticPage.html", {})