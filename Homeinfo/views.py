from django.shortcuts import render

# Create your views here.

def home(request):
    """Vista principal de la aplicación PawsToHome"""
    return render(request, 'Homeinfo/home.html')
