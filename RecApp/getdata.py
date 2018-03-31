import csv, random, os
import django
import pandas as pd
import py2neo
import json
import requests
from models import *
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty, RelationshipTo,
                      RelationshipFrom,db)
from py2neo import Graph, Node, Relationship

# graph = Graph('http://localhost:11001/db/data')
config.DATABASE_URL = 'bolt://neo4j:Test@localhost:11002'
main_api = "https://developers.zomato.com/api/v2.1/"
header = {'X-Zomato-API-Key': "4138367c7bc3dcc4e3bd4f964514c622"}

def returnresponse(url):
	response = requests.get(url,headers = header)
	return response.json()
	
def get_cuisines():
	url  = main_api + 'cuisines?city_id=4'
	data = returnresponse(url)
	num = len(data["cuisines"])
	for i in range(0,num):
		var = data["cuisines"][i]["cuisine"]
		var["cuisine_name"] = Cuisine(cid = var["cuisine_id"], name = var["cuisine_name"]).save()


def get_restaurants_add_links():
        url = main_api + 'search?start=0&q=Bangalore&lat=12.9716&lon=77.5946'
        data = returnresponse(url)
        for i in range(0,20):
                var = data["restaurants"][i]["restaurant"]
                var["id"] = Restaurant(rid = var["id"],name = var["name"],pno = var["phone_no"],rating = var["user_rating"]["aggregate_rating"]).save()
                cuisines = []
                cuisines = var["cuisines"].split(',')
                for j in range(0,len(cuisines)):
                    cuisine_node = Cuisine.nodes.get(name = cuisines[j].strip())
                    var["id"].SERVES.connect(cuisine_node)
		try:
			name = Location.nodes.get(locality =var['location']['locality'])
		except Location.DoesNotExist:
			data["locality"] = Location(locality = var['location']['locality']).save()
		loc = Location.nodes.get(locality=var['location']['locality'])
		var["id"].In.connect(loc,{'addr':var['location']['address'],'lat':var['location']['latitude'],'long':var['location']['longitude'],\
					  'zipcode':var['location']['zipcode']})

def find_res_with_cuisine():
        query = """MATCH (n:Restaurant)-[:SERVES]->(c:Cuisine)<-[:SERVES]-(m:Restaurant)
                   WHERE n<>m 
                   WITH n,COLLECT(c.name) AS CUISINES,m return n.name,CUISINES,m.name"""
        r,res = db.cypher_query(query)
        for i in range(0,len(r)):
            print(r[i])

get_restaurants()
