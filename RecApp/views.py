from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
def index(request):
        return render(request,'RecApp/main_page.html')
def signup(request):
        return render(request,'RecApp/signup.html')
