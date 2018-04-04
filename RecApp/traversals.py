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

def colaborative():
    query = "MATCH (p1:User)-[x:RATED]->(r:Restaurant)<-[y:RATED]-(p2:User) WITH SUM(x.rating * y.rating) AS xyDotProduct,\
    SQRT(REDUCE(xDot = 0.0, a IN COLLECT(x.rating) | xDot + a^2)) AS xLength,\
    SQRT(REDUCE(yDot = 0.0, b IN COLLECT(y.rating) | yDot + b^2)) AS yLength,p1, p2 MERGE (p1)-[s:SIMILARITY]-(p2)\
    SET s.similarity = xyDotProduct / (xLength * yLength)"
    r,res = db.cypher_query(query)
    query1 = "MATCH (p1:User {name:'Aishwarya'})-[s:SIMILARITY]-(p2:User) WITH p2, s.similarity AS sim ORDER BY sim DESC LIMIT 5 \
    RETURN p2.name AS Neighbor, sim AS Similarity"
    r1,res = db.cypher_query(query1)
    for i in range(0,len(r1)):
        print(r1[i])

colaborative()

def weighted_content(cuisine,loc):
    params = {
        'cuisine':cuisine,
        'loc' : loc,
    }
    query = "MATCH (c:Cuisine) WHERE c.name ='" + cuisine + "'MATCH (r:Restaurant)-[:SERVES]->(c) \
    WITH r, COUNT(*) AS gs \
    OPTIONAL MATCH (r)-[i:IN]->(l:Location {locality:'"+loc+"'}) WITH r, gs, COUNT(i) AS as \
    RETURN r.name AS recommendation, (5*gs)+(3*as) AS score ORDER BY score DESC LIMIT 100"
    r,res = db.cypher_query(query,params)
    for i in range(0, len(r)):
        print(r[i])

weighted_content('American','Church Street')
#find_res_with_cusine_para(['Italian','American'])	
#friend_similarity(sys.argv[1],sys.argv[2])
