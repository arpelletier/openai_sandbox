from neo4j import GraphDatabase, RoutingControl
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import re


def get_node_type_properties():
    """
    This function returns the node schema of the graph.
    The results are returned as nodeType to a list of protertyName (node features)
    """
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        result = driver.execute_query("call db.schema.nodeTypeProperties", database_="neo4j",
                                      routing_=RoutingControl.READ)

        # Extract nodeType and propertyName using regular expressions
        records = re.findall(r"nodeType='([^']+)'.*?propertyName='([^']+)'", str(result))

        # Create a dictionary from the extracted values
        node_type_to_property = {nodeType.replace('`', '').replace(':', ''): propertyName for nodeType, propertyName in
                                 records}

        return node_type_to_property


def get_rel_types():
    """
    This function returns the relationship types in the graph as a list.
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        query = '''MATCH ()-[r]->()
        RETURN DISTINCT type(r) AS relationshipType;
        '''
        result = driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)

        # Extract relationshipType values using regular expressions
        relationship_types = re.findall(r"relationshipType='(.*?)'", str(result))

        return relationship_types


def get_uniq_relation_pairs():
    """
    This function returns the unique relationships and the node types it connects.
    """

    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        query = '''MATCH (n1)-[r]->(n2)
        RETURN DISTINCT type(r) AS relationshipType, labels(n1) AS nodeType1, labels(n2) AS nodeType2;
        '''

        result = driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)

        # Define a regular expression pattern to match the relevant information
        pattern = r"relationshipType='(.*?)' nodeType1=\[(.*?)\] nodeType2=\[(.*?)\]"

        # Use the re.findall() function to extract matches
        matches = re.findall(pattern, str(result))

        # Create a list of tuples (nodeType1, relationshipType, nodeType2) #TODO double check this logic
        res = [(match[1].split(', ')[0].replace("'", ""), match[0], match[2].split(', ')[0].replace("'", "")) for match
               in matches]

        return res


def find_disease_name(mesh_ids):
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        query = '''MATCH (disease:MeSH_Disease {name: 'MeSH_Disease:%s'})
        RETURN disease
        ''' % (list(mesh_ids.values())[0][0])
        print(query)
        result = driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)
        print(result)


def get_diseases(mesh_ids):
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        query = '''MATCH (disease:MeSH_Disease)
        RETURN disease LIMIT 50
        '''

        result = driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)
        return result
        #         print(result)


temp = get_diseases(mesh_ids)

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


def query():
    test_input = 'MATCH (tom:Person {name: "Tom Hanks"})-[:ACTED_IN]->(tomHanksMovies)\nRETURN tom,tomHanksMovies'
    return search(test_input)


def interactive():
    while True:
        # Get user input
        user_input = input("Query (q); Delete (d); Populate (p)")

        if user_input == 'q':
            print("Query.")
            result = query()
        elif user_input == 'd':
            print("Delete.")
            # result = clear_neo4j()
        elif user_input == 'p':
            print("Populate.")
            # result = populate_temp()

        print(result)


if __name__ == "__main__":
    interactive()
# print(get_node_type_properties())
