from django.shortcuts import render
from django.urls import reverse

from RecApp.forms import get_reco_form, rate_rest_form
import random
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.
from neomodel import db, config
config.DATABASE_URL = 'bolt://neo4j:aishwarya@localhost:7687'
from RecApp.traversals import weighted_content, collaborative


def index(request):
        return render(request,'RecApp/main_page.html')
def signup(request):
        return render(request,'RecApp/signup.html')
def min(a,b):
        if a<b:
                 return a
        return b
def recommend(request):
        form = get_reco_form()
        final_weight_list= []
        final_list =[]
        if request.method == 'POST':
                username = request.POST.get('name')
                cuisine = request.POST.get('cuisine')
                location = request.POST.get('location')
                price = request.POST.get('price')
                weighted_list = weighted_content(username,float(cuisine),float(location),float(price))
                final_weight_list = random.sample(weighted_list,min(5,len(weighted_list)))
                final_weight_list = [x[0] for x in final_weight_list]
                co_list = collaborative(username)
                final_list = final_weight_list
                co_list = [x[0] for x in co_list]
                for x in co_list:
                        if x not in final_list:
                                final_list.append(x)
                random.shuffle(final_list)
                return render(request,'RecApp/result.html',{'final_list':final_list[:10]})
        return render(request,'RecApp/recommendations.html',{'form':form})

def rate(request):
        form = rate_rest_form()
        if request.method == 'POST':
                username = request.POST.get('username')
                rname = request.POST.get('restaurant_name')
                location = request.POST.get('location')
                rating = request.POST.get('rating')
                params = {
                        'rname':rname,
                        'loc':location,
                        'username':username,
                        'rating':float(rating),
                }
                query = "MATCH (r:Restaurant)-[l:IN]->(l1:Location) WHERE r.name=$rname and l1.locality=$loc with r \
                MATCH (u:User {name:$username}) with u, r MERGE (u)-[ra:RATED]->(r) SET ra.rating=$rating"
                res,meta = db.cypher_query(query,params)
                msg = "Rating has been recorded!"
                messages.add_message(request,messages.INFO,msg)
                return HttpResponseRedirect(reverse('index'))
        return render(request,'RecApp/rating.html',{'form':form})
