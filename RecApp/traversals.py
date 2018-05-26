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

def get_top_restaurant(uname):
    params = {
        'uname':uname,
    }
    query = "MATCH (U:User {name:$uname})-[r:RATED]->(res:Restaurant) with max(r.rating) as MAX_RATING \
    MATCH (U:User {name:$uname})-[r:RATED]->(res:Restaurant) where r.rating = MAX_RATING return res.rid order by rand() limit 2 "
    result,meta = db.cypher_query(query,params)
    return result

def jaccard_similarity(uname):
    rlist= get_top_restaurant(uname)
    for rid in rlist:
        params = {
            'rid':rid[0],
        }
        """Find similar restaurants in terms of price range, cuisine and locality"""
        query = "MATCH (r:Restaurant {rid:$rid})-[:SERVES|:IN|:WITH_COST]->(n)<-[:SERVES|:IN|:WITH_COST]-(other:Restaurant)\
                    WHERE r.name <> other.name\
                    with r,other,count(n) as intersection \
                    MATCH (r)-[:SERVES|:IN|:WITH_COST]->(r1)\
                    with r,other,intersection,collect(distinct(id(r1))) as u1\
                    MATCH (other)-[:SERVES|:IN|:WITH_COST]->(r2) \
                    with r,other,intersection,u1,collect(distinct(id(r2))) as u2 \
                    with r,other,intersection,u1,u2 \
                    with r,other,intersection,u1 + filter(x in u2 WHERE NOT  x IN u1) as union ,u1,u2 \
                    return r.rid,other.rid,((1.0*intersection)/(size(union))) as jaccard order by jaccard desc limit 3"
        res, meta = db.cypher_query(query,params)
        for i in range(0, len(res)):
            print(res[i])
        return res


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

def weighted_content(uname,cuisine,loc):
    rlist = jaccard_similarity(uname)
    for id in rlist:
        print(id[1])
        params = {
            'orig_id' = id[0],
            'other_id' = id[1],
        }
        query = "MATCH (r:Restaurant{rid:$other_id})-[:SERVES]->(c)<-[:SERVES]-(other:Restaurant) where r<>other and other.rid<>$orig_id\
        with r,other,count(c) as c_count\
        MATCH (r:Restaurant{rid:$other_id})-[:IN]->(l)<-[:IN]-(other:Restaurant) where r<>other and other.rid<>$orig_id\
                with r,other,c_count,count(l) as l_count\
        RETURN r.name AS recommendation, (5*c_count)+(3*l_count) AS score ORDER BY score DESC LIMIT 10"

        r,res = db.cypher_query(query,params)
        for i in range(0, len(r)):
            print(r[i])

weighted_content('Soumya',6,7)
#colaborative('Saloni')
#jaccard_similarity('Soumya')
#friend_similarity(sys.argv[1],sys.argv[2])