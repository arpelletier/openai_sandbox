import pandas as pd
from neo4j import GraphDatabase, RoutingControl

neo4j_uri = "neo4j+s://d1751857.databases.neo4j.io"  # The default URI for Neo4j
neo4j_user = "neo4j"
neo4j_password = "Nwb27DK-3SuiqTAaW01VjVKRN_mnEgDLqQDVpPncVAI"

def get_schema():
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        return driver.execute_query("call db.schema.nodeTypeProperties", database_="neo4j", routing_=RoutingControl.READ)

if __name__ == "__main__":
    print(get_schema())