import pandas as pd
from neo4j_api import GraphDatabase, RoutingControl

neo4j_uri = "neo4j_api+s://d1751857.databases.neo4j_api.io"  # The default URI for Neo4j
neo4j_user = "neo4j_api"
neo4j_password = "Nwb27DK-3SuiqTAaW01VjVKRN_mnEgDLqQDVpPncVAI"

def get_schema():
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        return driver.execute_query("CALL db.schema.nodeTypeProperties", database_="neo4j", routing_=RoutingControl.READ)
    
def get_node_labels():
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        return driver.execute_query("CALL db.labels()", database_="neo4j", routing_=RoutingControl.READ)
    
def get_relationship_types():
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        return driver.execute_query("CALL db.relationshipTypes()", database_="neo4j", routing_=RoutingControl.READ)

if __name__ == "__main__":
    print("GRAPH SCHEMA")
    print(get_schema())
    print("NODE TYPES")
    print(get_node_labels())
    print("RELATIONSHIP TYPES")
    print(get_relationship_types())