from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.http import JsonResponse
from .models import Profile, Like
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
    if request.method == "GET":
        db = dbConnection()
        users = db["authenticate"]
        user_data = users.find_one({"isActive": 1})
        if user_data:
            auth_token = request.COOKIES.get('auth_token')
            stored_auth_token = user_data.get("auth_token")
            if auth_token:
                if stored_auth_token == hashlib.sha256(auth_token.encode()).hexdigest():
                    return redirect('staticPage')

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
            # If no auth token in cookie, proceed with regular login process
            if hashed_password == stored_hashed_password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    auth_token = secrets.token_urlsafe(32)
                    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
                    users.update_one({"username": username}, {"$set": {"auth_token": hashed_token, "isActive": 1}})
                    response = redirect('staticPage')
                    response.set_cookie('auth_token', auth_token, httponly=True, max_age=3600)
                    return response
                else:
                    messages.error(request, "Bad Credentials")
                    
    return render(request, "loginPage.html", context)

def logoutRequest(request):
    logout(request)
    db = dbConnection()
    users = db["authenticate"]
    users.update_one({"isActive": 1}, {"$set": {"isActive": 0}})
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

        users.insert_one({"username": username, "salt": salt, "hashed_password": hashed_password, "auth_token": "", "isActive": 0})
        
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
            db = dbConnection()
            users = db["authenticate"]
            users.update_one({"isActive": 1}, {"$set": {"isActive": 0}})
            response = redirect('loginPage')
            response.delete_cookie('auth_token')
            return response
    else:
        logout(request)
        db = dbConnection()
        users = db["authenticate"]
        users.update_one({"isActive": 1}, {"$set": {"isActive": 0}})
        response = redirect('loginPage')
        response.delete_cookie('auth_token')
        return response
    return render(request, "staticPage.html", {})

@login_required(login_url='loginPage')
def homePage(request):
    db = dbConnection()
    profiles = db["Profiles"]
    user = request.user
    username = user.username
    emptyProfile = {"name": "", "gender": "", "location": "", "bio": "", "likes": 0}
    if request.method == 'POST':
        name = username
        gender = request.POST.get('Gender')
        location = request.POST.get('Location')
        bio = request.POST.get('Bio')
        profile = {"name": name, "gender": gender, "location": location, "bio": bio, "likes": 0}
        profiles.insert_one(profile)
    random_profile = profiles.aggregate([{ '$sample': { 'size': 1 } }])
    random_profile = list(random_profile)
    if random_profile:
        random_profile = random_profile[0]
    else:
        random_profile = emptyProfile
    return render(request, 'homePage.html', {'random_profile': random_profile})

def nextProfile(request):
    return redirect('homePage')

def likeProfile(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        profile_name = request.POST.get('profile_name')
        db = dbConnection()
        likes_collection = db["likes"]
        user_likes = likes_collection.find_one({"username": username})
        if user_likes:
            liked_profiles = user_likes.get("liked_profiles", [])
            if profile_name not in liked_profiles:
                likes_collection.update_one({"username": username}, {"$push": {"liked_profiles": profile_name}})
                profiles_collection = db["Profiles"]
                profile = profiles_collection.find_one({"name": profile_name})
                if profile:
                    profiles_collection.update_one({"name": profile_name}, {"$inc": {"likes": 1}})
        else:
            likes_collection.insert_one({"username": username, "liked_profiles": [profile_name]})
            profiles_collection = db["Profiles"]
            profile = profiles_collection.find_one({"name": profile_name})
            if profile:
                profiles_collection.update_one({"name": profile_name}, {"$inc": {"likes": 1}})
    return redirect('homePage')