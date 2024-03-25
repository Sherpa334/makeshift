from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
import bcrypt
import hashlib
import secrets

def dbConnection():
    mongo_client = MongoClient("mongo")
    db = mongo_client["makeshift"]
    return db

# Create your views here.
def loginPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        db = dbConnection()
        users = db["authenticate"]
        user_data = users.find_one({"username": username})
        if user_data:
            salt = user_data.get("salt")
            stored_hashed_password = user_data.get("hashed_password")

            hashed_password = bcrypt.hashpw(password.encode(), salt)

            user = authenticate(username=username, password=password)

            if hashed_password == stored_hashed_password and user is not None:
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
        db = dbConnection()
        users = db["authenticate"]
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username) or users.find_one({"username": username}):
            messages.error(request, "Username already exist")
            return render(request, "registerPage.html", context)

        if password != confirm_password:
            messages.error(request, "Passwords didn't match")
            return render(request, "registerPage.html", context)
        
        salt = bcrypt.gensalt()

        hashed_password = bcrypt.hashpw(password.encode(), salt)
        
        user = User.objects.create_user(username=username, password=password)
        user.save()

        users.insert_one({"username": username, "salt": salt, "hashed_password": hashed_password})
        
        messages.success(request, "Account creation is successful")
        return redirect('loginPage')
    
    return render(request, "registerPage.html", context)

@login_required(login_url='loginPage')
def staticPage(request):
    return render(request, "staticPage.html", {})