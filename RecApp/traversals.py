from neomodel import db, config

config.DATABASE_URL = 'bolt://neo4j:aishwarya@localhost:7687'

def friend_similarity(uname, rate):
    params = {
        'name': uname,
        'rate_res': float(rate),
    }

    """Find Restaurants that my friends have rated 3 and above and that serve the cuisines that I like"""
    query = """	MATCH (u:User{name:$name})-[FRIENDS]->(rec:User),
				(rec)-[r:RATED]-(res:Restaurant),(u)-[l:LIKES]->(c:Cuisine)<-[:SERVES]-(res) 
				where r.rating > $rate_res with res,r return res.name"""
    res, meta = db.cypher_query(query, params)
    for i in range(0, len(res)):
        print(res[i])


def jaccard_similarity(rlist):
    for rname in rlist:
        params = {
            'rname':rname,
        }
        """Find similar restaurants in terms of price range, cuisine and locality"""
        query = "MATCH (r:Restaurant {name:'"+rname+"'})-[:SERVES|:IN|:WITH_COST]->(n)<-[:SERVES|:IN|:WITH_COST]-(other:Restaurant)\
                    with r,other,count(n) as intersection \
                    MATCH (r)-[:SERVES|:IN|:WITH_COST]->(r1)\
                    with r,other,intersection,collect(distinct(id(r1))) as u1\
                    MATCH (other)-[:SERVES|:IN|:WITH_COST]->(r2) \
                    with r,other,intersection,u1,collect(distinct(id(r2))) as u2 \
                    with r,other,intersection,u1,u2 \
                    with r,other,intersection,u1 + filter(x in u2 WHERE NOT  x IN u1) as union ,u1,u2 \
                    return r.name,other.name,((1.0*intersection)/(size(union))) as jaccard order by jaccard desc limit 3"
        res, meta = db.cypher_query(query)
        for i in range(0, len(res)):
            print(res[i])


def colaborative(uname):
    params ={
        'uname':uname,
    }
    query = "MATCH (p1:User {name:'"+uname+"'})-[x:RATED]->(rest:Restaurant)<-[y:RATED]-(p2:User) WITH SUM(x.rating * y.rating) AS xyDotProduct,\
    count(rest) as c,\
    SQRT(REDUCE(xDot = 0.0, a IN COLLECT(x.rating) | xDot + a^2)) AS xLength,\
    SQRT(REDUCE(yDot = 0.0, b IN COLLECT(y.rating) | yDot + b^2)) AS yLength,p1, p2 MERGE (p1)-[s:SIMILARITY]-(p2)\
    SET s.similarity = (xyDotProduct) / (xLength * yLength),s.count = c"
    r,res = db.cypher_query(query)
    query1 = "MATCH (p1:User {name:'"+uname+"'})-[s:SIMILARITY]-(p2:User) WITH p2, s.similarity AS sim,s.count as c ORDER BY sim*c DESC LIMIT 5 \
    RETURN p2.name AS Neighbor, sim AS Similarity"
    r1,res = db.cypher_query(query1)
    for i in r1:
        print(i)
        query2 = "MATCH (o:User {name: '"+i[0]+"'})-[r:RATED]->(rec:Restaurant)\
                    MATCH (u:User{name: '"+uname+"'}) WHERE NOT EXISTS( (u)-[:RATED]->(rec) ) AND r.rating > 4 RETURN rec.name"
        r3,res = db.cypher_query(query2)
        for j in range(0,len(r3)):
            print(r3[j])
    query3 = "MATCH (p1:User {name:'"+uname+"'})-[s:SIMILARITY]-() DELETE s"
    r3,res=db.cypher_query(query3)

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

#weighted_content('American','Church Street')
#colaborative('Saloni')
#jaccard_similarity(['Koramangala Social','Paakashala'])
#friend_similarity(sys.argv[1],sys.argv[2])