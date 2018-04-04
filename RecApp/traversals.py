import csv, random, os
import django
import sys
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

def find_res_with_cuisine():
		"""Find restaurants that serve same cuisine"""
		query = """
					MATCH (n:Restaurant)-[:SERVES]->(c:Cuisine)<-[:SERVES]-(m:Restaurant)
					WHERE n<>m 
					WITH n,COLLECT(c.name) AS CUISINES,m return n.name,CUISINES,m.name
				"""
		r,res = db.cypher_query(query)
		for i in range(0,len(r)):
			print(r[i])

def friend_similarity(uname,rate):
	params = {
	'name' : uname,
	'rate_res' : float(rate),
	}
	
	"""Find Restaurants that my friends have rated 3 and above and that serve the cuisines that I like"""
	query = """	MATCH (u:User{name:$name})-[FRIENDS]->(rec:User),
				(rec)-[r:RATED]-(res:Restaurant),(u)-[l:LIKES]->(c:Cuisine)<-[:SERVES]-(res) 
				where r.rating > $rate_res with res,r return res.name"""
	res,meta = db.cypher_query(query,params)
	for i in range(0,len(res)):
		print(res[i])
	
def find_res_with_cusine_para(cuisine):
    for j in cuisine:
        query = "MATCH (n:Restaurant)-[:SERVES]->(c:Cuisine) WHERE c.name='" + j + "' RETURN n.name,c.name"
        r, res = db.cypher_query(query)
        for i in range(0, len(r)):
            print(r[i])

def jaccard_similarity(rname):
	"""Find similar restaurants in terms of price range, cuisine and locality"""
	query = """MATCH (r:Restaurant)-[:SERVES|:IN|:WITH_COST]->(n)<-[:SERVES|:IN|:WITH_COST]-(other:Restaurant)
				with r,other,count(n) as intersection 
				MATCH (r)-[:SERVES|:IN|:WITH_COST]->(r1)
				with r,other,intersection,collect(distinct(id(r1))) as u1
				MATCH (other)-[:SERVES|:IN|:WITH_COST]->(r2)
				with r,other,intersection,u1,collect(distinct(id(r2))) as u2
				with r,other,intersection,u1,u2
				with r,other,intersection,u1 + filter(x in u2 WHERE NOT  x IN u1) as union ,u1,u2
				return r.name,other.name,((1.0*intersection)/(size(union))) as jaccard order by jaccard desc limit 20"""
	res,meta = db.cypher_query(query)
	for i in range(0,len(res)):
		print(res[i])
			
jaccard_similarity("Farzi Cafe")
#find_res_with_cusine_para(['Italian','American'])	
#friend_similarity(sys.argv[1],sys.argv[2])
