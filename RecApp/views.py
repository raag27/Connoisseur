from django.shortcuts import render
from RecApp.forms import get_reco_form
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from RecApp.traversals import weighted_content


def index(request):
        return render(request,'RecApp/main_page.html')
def signup(request):
        return render(request,'RecApp/signup.html')

def recommend(request):
        form = get_reco_form()
        print("hello")
        if request.method == 'POST':
                username = request.POST.get('name')
                cuisine = request.POST.get('cuisine')
                location = request.POST.get('location')
                weighted_content(cuisine,location)
        return render(request,'RecApp/recommendations.html',{'form':form})