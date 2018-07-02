import sys
import requests
import json
import csv
import urllib

from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty, RelationshipTo,
                      RelationshipFrom, db)
from py2neo import Graph, Node, Relationship

# graph = Graph('http://localhost:11001/db/data')
config.DATABASE_URL = 'bolt://neo4j:aishwarya@localhost:7687'

main_api = "https://developers.zomato.com/api/v2.1/"
header = {'X-Zomato-API-Key': "4138367c7bc3dcc4e3bd4f964514c622"}
from models import Restaurant,Cuisine,Location,User

def returnresponse(url):
    response = requests.get(url, headers=header)
    return response.json()

def read(opfile):
    reader = csv.reader(opfile)
    included_cols = [0, 1, 2, 3]
    for row in reader:
        content = list(row[i] for i in included_cols)
        url = main_api + 'search?q=' + content[1]
        data = returnresponse(url)
        for r in range(0, len(data["restaurants"])):
            var = data["restaurants"][r]["restaurant"]
            if var["location"]["locality"].find(content[2]) != -1:
                try:
                    Restaurant.nodes.get(rid=var["id"])
                except Restaurant.DoesNotExist:
                    Restaurant(rid=var["id"], name=var["name"], rating=var["user_rating"]["aggregate_rating"],
                               ratings_count=var["user_rating"]["votes"], avg_cost=var["average_cost_for_two"],
                               url=var["url"], has_online_delivery=var["has_online_delivery"],
                               has_table_booking=var["has_table_booking"]).save()
                    rest = Restaurant.nodes.get(rid=var["id"])
                    cuisines = var["cuisines"].split(',')
                    for j in range(0, len(cuisines)):
                        cuisine_node = Cuisine.nodes.get(name=cuisines[j].strip())
                        rest.SERVES.connect(cuisine_node)

                    var_loc = var["location"]
                    try:
                        Location.nodes.get(locality=var_loc["locality"])
                    except Location.DoesNotExist:
                        Location(locality=var_loc["locality"]).save()
                    loc = Location.nodes.get(locality=var_loc["locality"])
                    rest.IN.connect(loc, {'addr': var_loc['address'], 'lat': var_loc['latitude'],
                                          'long': var_loc['longitude'], \
                                          'zipcode': var_loc['zipcode']})
                rest = Restaurant.nodes.get(rid=var["id"])
                if content[0] != " ":
                    try:
                        User.nodes.get(name=content[0])
                        print("hello")
                    except User.DoesNotExist:
                        User(name=content[0]).save()
                u = User.nodes.get(name=content[0])
                u.RATED.connect(rest, {'rating': content[3]})
                break
def friend(opfile):
    reader = csv.reader(opfile)
    included_cols = [0,1]
    for row in reader:
        content = list(row[i] for i in included_cols)
        u = User.nodes.get(name=content[0])
        u1 = User.nodes.get(name=content[1])
        u.FRIEND.connect(u1)

def create_node():
    opfile = open('C:/Users/hiremath/New folder/ZomatoUserData.csv', 'r')
    #read(opfile)
    friend(opfile)


#create_node()

