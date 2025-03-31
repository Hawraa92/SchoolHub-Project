from django.shortcuts import render
from django.http import HttpResponse

def dashboard(request):
    return HttpResponse("Welcome to the Teachers Dashboard!")

def profile(request):
    return HttpResponse("This is the Teachers Profile Page!")
