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
				var["id"] = Restaurant(rid = var["id"],name = var["name"],rating = var["user_rating"]["aggregate_rating"],ratings_count = var["user_rating"]["votes"],avg_cost = var["average_cost_for_two"],url = var["url"],has_online_delivery = var["has_online_delivery"],has_table_booking = var["has_table_booking"]).save()

				cuisines = []
				cuisines = var["cuisines"].split(',')
				for j in range(0,len(cuisines)):
					cuisine_node = Cuisine.nodes.get(name = cuisines[j].strip())
					var["id"].SERVES.connect(cuisine_node)
				
				var_loc = var["location"]
				try:
					loc = Location.nodes.get(locality = var_loc["locality"])
				except Location.DoesNotExist:
					loc = Location(locality = var_loc["locality"]).save()
				var["id"].IN.connect(loc,{'addr':var_loc['address'],'lat':var_loc['latitude'],'long':var_loc['longitude'],\
				'zipcode':var_loc['zipcode']})

def get_user():
    f = open('C:/Users/Raagini/Desktop/Amazon-RestaurantRecommender/Connoisseur/RecApp/User.csv', 'r')
    reader = csv.reader(f)
    flag = 0
    for row in reader:
        if flag == 0:
            flag = 1
        else:
            lists = row[0].split('\t')
            User(uid=lists[0],name=lists[1],phone_no = lists[2],email_id = lists[3],age = lists[4],gender=lists[5]).save()

    f.close()

def friends_relation():
    query = "MATCH (p1:User), (p2:User) WITH p1, p2 WHERE rand() < 0.1 AND p1<>p2 MERGE (p1)-[:FRIENDS]->(p2) RETURN DISTINCT p1, p2"
    results, meta = db.cypher_query(query)

def user_rated_restaurant():
	for i in range(1,15):
		rand_val= random.uniform(1,5)
		rand_val = round(rand_val,1)
		user,umeta = db.cypher_query("MATCH (p:User) return p.uid order by rand() limit 1")
		rest,rmeta = db.cypher_query("MATCH (r:Restaurant) return r.rid order by rand() limit 1")
		user_id = user[0][0]
		res_id = rest[0][0]
		params = {
			'user' : user_id,
			'rand_key' : rand_val,
			'restaurant' : res_id
		}
		query = "MATCH (u:User{uid : $user}),(r:Restaurant{rid:$restaurant}) WITH  u,r MERGE (u)-[ra:RATED]-(r) ON CREATE SET ra.rating = $rand_key return ra ORDER BY rand() LIMIT 1"
		results, meta = db.cypher_query(query,params)
	
def find_res_with_cuisine():
	
        query = """MATCH (n:Restaurant)-[:SERVES]->(c:Cuisine)<-[:SERVES]-(m:Restaurant)
                   WHERE n<>m 
                   WITH n,COLLECT(c.name) AS CUISINES,m return n.name,CUISINES,m.name"""
        r,res = db.cypher_query(query)
        for i in range(0,len(r)):
            print(r[i])

user_rated_restaurant()