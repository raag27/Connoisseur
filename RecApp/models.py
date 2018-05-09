from django.db import models
from neomodel import (BooleanProperty, config, JSONProperty, FloatProperty, StructuredNode, StructuredRel, \
                      StringProperty, IntegerProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom,
                      EmailProperty, Relationship)
# Create your models here.
# config.DATABASE_URL = 'bolt://neo4j:Recommender@localhost:11002'

class Price(StructuredNode):
    cost = FloatProperty(unique=True,required=False)


class Cuisine(StructuredNode):
    cid = UniqueIdProperty()
    name = StringProperty()


class Location(StructuredNode):
    locality = StringProperty()


class Locrel(StructuredRel):
    addr = StringProperty(required=True)
    lat = FloatProperty()
    long = FloatProperty()
    # zipcode = IntegerProperty(NULL = True)


class Restaurant(StructuredNode):
    rid = UniqueIdProperty()
    name = StringProperty()
    avg_cost = FloatProperty()
    rating = FloatProperty()
    ratings_count = IntegerProperty()
    url = StringProperty()
    has_online_delivery = BooleanProperty()
    has_table_booking = BooleanProperty()

    SERVES = RelationshipTo(Cuisine, 'SERVES')
    IN = RelationshipTo(Location, 'IN', model=Locrel)
    WITH = RelationshipTo(Price, 'WITH_COST')

class Rated(StructuredRel):
    rating = FloatProperty()


class Liked(StructuredRel):
    liking = IntegerProperty()


class Sim(StructuredRel):
    similarity = FloatProperty()
    count = IntegerProperty()

class User(StructuredNode):
    name = StringProperty()
    FRIEND = Relationship('User', 'FRIENDS')
    RATED = RelationshipTo(Restaurant, 'RATED', model=Rated)
    LIKES = RelationshipTo(Cuisine, 'LIKES', model=Liked)
    SIM = RelationshipTo(Restaurant, 'SIMILARITY', model=Sim)




