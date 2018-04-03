from django.db import models
from neomodel import (BooleanProperty,config,JSONProperty,FloatProperty,StructuredNode, StructuredRel,StringProperty, IntegerProperty,UniqueIdProperty, RelationshipTo, RelationshipFrom,EmailProperty,Relationship)
# Create your models here.
# config.DATABASE_URL = 'bolt://neo4j:Recommender@localhost:11002'

class Cuisine(StructuredNode):
    cid = UniqueIdProperty()
    name = StringProperty()

class Location(StructuredNode):
    locality = StringProperty()

class Locrel(StructuredRel):
    addr = StringProperty(required=True)
    lat = FloatProperty()
    long = FloatProperty()
    #zipcode = IntegerProperty(NULL = True)

class Restaurant(StructuredNode):
    rid = UniqueIdProperty()
    name = StringProperty()
    avg_cost = FloatProperty()
    rating = FloatProperty()
    ratings_count  = IntegerProperty()
    url = StringProperty()
    has_online_delivery = BooleanProperty()
    has_table_booking = BooleanProperty()

    SERVES = RelationshipTo(Cuisine,'SERVES')
    IN = RelationshipTo(Location,'IN',model=Locrel)

    def find_res_with_cuisine(self):
        query = """MATCH (n:Restaurant)->[:SERVES]->(c:Cuisine)<-[:SERVES]<-(m:Restaurant)
                   WHERE n<>m 
                   COLLECT(c.name) AS CUISINES return CUISINES,m"""
        res = self.cypher(query)
        print(res)
    #IN = RelationshipTo(Location,'IN')

class Rated(StructuredRel):
    rating = FloatProperty()

class Liked(StructuredRel):
    liking = IntegerProperty()

class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty()
    phone_no = StringProperty()
    email_id = EmailProperty()
    age = IntegerProperty()
    gender = StringProperty()

    FRIEND = Relationship('User','FRIENDS')
    RATED = RelationshipTo(Restaurant,'RATED',model = Rated)
    LIKES = RelationshipTo(Cuisine,'LIKES',model = Liked)
