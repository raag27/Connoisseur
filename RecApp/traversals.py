def find_res_with_cuisine():
        query = """MATCH (n:Restaurant)-[:SERVES]->(c:Cuisine)<-[:SERVES]-(m:Restaurant)
                   WHERE n<>m 
                   WITH n,COLLECT(c.name) AS CUISINES,m return n.name,CUISINES,m.name"""
        r,res = db.cypher_query(query)
        for i in range(0,len(r)):
            print(r[i])
