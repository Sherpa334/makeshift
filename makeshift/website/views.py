from django.shortcuts import render

# Create your views here.
def loginPage(request):
    return render(request, "loginPage.html", {})
def staticPage(request):
    return render(request, "staticPage.html", {})