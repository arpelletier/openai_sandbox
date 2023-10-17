from neo4j import GraphDatabase, RoutingControl
import sys

# The the URI by looking at the Connection URI of the specific instance
URI = "neo4j+s://d1751857.databases.neo4j.io"
# User is typically "neo4j"
USER = "neo4j"
# Password is generated when initially 
PASSWORD = "Nwb27DK-3SuiqTAaW01VjVKRN_mnEgDLqQDVpPncVAI"
# Define authorizations
AUTH = (USER, PASSWORD)


def get_node_type_properties():
    """
    Return node schema. 
    In practice, send this output to Chat GPT so it knows what the names of certain node properties are.
    The output will appear verbose, but there does not seem to be a better way of doing this at the moment.
    """
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        return driver.execute_query("call db.schema.nodeTypeProperties", database_="neo4j", routing_=RoutingControl.READ)

def search_query(driver, query):
    """Return search query."""
    return driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ) 

def search(query):
    """Search the graph database using a query."""
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Verify working connection
        try:
            driver.verify_connectivity()
        except Exception as e:
            print("Unable to verify connection.")
            print("Error: {}".format(e))
        # Attempt search query
        return search_query(driver, query)

if __name__ == "__main__":
    print(get_node_type_properties())