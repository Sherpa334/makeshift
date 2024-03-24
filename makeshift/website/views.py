from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.contrib import messages

# Create your views here.
def loginPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, "", context)
        else:
            messages.error(request, "Bad Credentials")
    return render(request, "loginPage.html", context)
    
def registerPage(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            messages.success(request, "Account creation is successful")
            return redirect('loginPage')
        except IntegrityError:
            messages.error(request, "Username already exists. Please choose a different username.")
    return render(request, "registerPage.html", context)