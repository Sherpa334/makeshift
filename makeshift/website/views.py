from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re
import hashlib
import secrets
# Create your views here.
def loginPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            auth_token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
            user.auth_token = hashed_token
            user.save()
            response = redirect('staticPage')
            response.set_cookie('auth_token', auth_token, httponly=True, max_age=3600)  
            return response
        else:
            messages.error(request, "Bad Credentials")
    return render(request, "loginPage.html", context)
def logout(request):
    logout(request)
    response = redirect('loginPage')
    response.delete_cookie('auth_token')
    return response  
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
        
        user = User.objects.create_user(username, None, password)
        
        user.save()
        messages.success(request, "Account creation is successful")
        return redirect('loginPage')
    
    return render(request, "registerPage.html", context)
@login_required(login_url='loginPage')
def staticPage(request):
    return render(request, "staticPage.html", {})