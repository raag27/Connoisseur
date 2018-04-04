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

def friends_relation():
    query = "MATCH (p1:User), (p2:User) WITH p1, p2 WHERE rand() < 0.1 AND p1<>p2 MERGE (p1)-[:FRIENDS]->(p2) RETURN DISTINCT p1, p2"
    results, meta = db.cypher_query(query)

def rated_relation():
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

def likes_relation():
	for i in range(1,30):
		user,umeta = db.cypher_query("MATCH (p:User) return p.uid order by rand() limit 1")
		cuisine,rmeta = db.cypher_query("MATCH (c:Cuisine) return c.cid order by rand() limit 1")
		user_id = user[0][0]
		c_id = cuisine[0][0]
		params = {
			'user':user_id,
			'cuisine':c_id,
			}
		query = "MATCH (u:User{uid : $user}),(c:Cuisine{cid:$cuisine}) WITH  u,c MERGE (u)-[l:LIKES]-(c) return l order by rand() LIMIT 1"
		results, meta = db.cypher_query(query,params)

def with_relation():
	query = """ MATCH (r:Restaurant) return r.rid """
	res,meta = db.cypher_query(query)
	for i in range (0,len(res)):
		n = Restaurant.nodes.get(rid = res[i][0])
		try:
			avg_cost = Price.nodes.get(cost  = n.avg_cost)
		except Price.DoesNotExist:
			avg_cost = Price(cost = n.avg_cost).save()
		n.WITH.connect(avg_cost)
		
		
	
with_relation()
#likes_relation()