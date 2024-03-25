from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.http import JsonResponse
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
    if request.user:
        username = request.user.username
        auth_token = request.COOKIES.get('auth_token')
        db = dbConnection()
        users = db["authenticate"]
        user_data = users.find_one({"username": username})
        stored_auth_token = user_data.get("auth_token")
        if auth_token:
            if stored_auth_token == hashlib.sha256(auth_token.encode()).hexdigest():
                    # If auth token matches, login the user and redirect to staticPage
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('staticPage')
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            else:
                return JsonResponse({'error': 'Invalid auth token'}, status=401)

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
            auth_token = request.COOKIES.get('auth_token')
            stored_auth_token = user_data.get("auth_token")
            if auth_token:
                if stored_auth_token == hashlib.sha256(auth_token.encode()).hexdigest():
                    # If auth token matches, login the user and redirect to staticPage
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('staticPage')
                    else:
                        return JsonResponse({'error': 'Invalid credentials'}, status=401)
                else:
                    return JsonResponse({'error': 'Invalid auth token'}, status=401)

            # If no auth token in cookie, proceed with regular login process
            if hashed_password == stored_hashed_password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    auth_token = secrets.token_urlsafe(32)
                    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
                    users.update_one({"username": username}, {"$set": {"auth_token": hashed_token}})
                    response = redirect('staticPage')
                    response.set_cookie('auth_token', auth_token, httponly=True, max_age=3600)
                    return response
                else:
                    messages.error(request, "Bad Credentials")
    return render(request, "loginPage.html", context)

def logoutRequest(request):
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

        users.insert_one({"username": username, "salt": salt, "hashed_password": hashed_password, "auth_token": ""})
        
        messages.success(request, "Account creation is successful")
        return redirect('loginPage')
    
    return render(request, "registerPage.html", context)

@login_required(login_url='loginPage')
def staticPage(request):
    if request.COOKIES.get('auth_token'):
        auth_token = request.COOKIES.get('auth_token')
        user = request.user
        username = user.username
        db = dbConnection()
        users = db["authenticate"]
        user_data = users.find_one({"username": username})
        stored_auth_token = user_data.get("auth_token")
        if stored_auth_token:
            if stored_auth_token != hashlib.sha256(auth_token.encode()).hexdigest():
                response = redirect('loginPage')
                return response
        else:
            logout(request)
            response = redirect('loginPage')
            response.delete_cookie('auth_token')
            return response
    else:
        logout(request)
        response = redirect('loginPage')
        response.delete_cookie('auth_token')
        return response
    return render(request, "staticPage.html", {})