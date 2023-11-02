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
        result = driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)

        return query, result


def verify_connection():
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        # Verify working connection
        try:
            driver.verify_connectivity()
        except Exception as e:
            print("Unable to verify connection.")
            print("Error: {}".format(e))
        return True


def search(query):
    """Return search query."""
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        try:
            return driver.execute_query(query, database_="neo4j", routing_=RoutingControl.READ)
        except Exception as e:
            print("Query was unsuccessful.")
            print("Error: {}".format(e))
            return False


def query():
    """Interactive query."""
    query = input("Enter a query: ")

    while True:
        if query == 'q':
            break
        else:
            result = search(query)

        # Enable user to enter another query if previous failed
        if not result:
            query = input("Enter a query: ")
        else:
            print(result)
            break


def get_user_prompt(options):
    """Return a user prompt based on the given options."""
    prompt = "Please select an option:\n"
    for key, value in options.items():
        prompt += f"{key}: {value[0]}\n"
    return prompt


def example_node(n=10):
    '''
    This function returns examples of nodes in the graph based on user selected node type.
    '''

    # Get user to specify node type for example
    print("Which node type do you want to see examples of?")
    node_to_prop = get_node_type_properties()
    idx_to_node = {idx: node for idx, node in enumerate(node_to_prop.keys())}
    for idx, node_type in idx_to_node.items():
        print(f"{idx}: {node_type}")

    user_input = input("Enter a number: ")
    while True:
        valid_input = int(user_input) in idx_to_node.keys()
        if valid_input:
            break
        else:
            print("Invalid input")
            user_input = input("Enter a number: ")

    # Make query
    query = '''MATCH (n:%s)
    RETURN n LIMIT %s
    ''' % (idx_to_node[int(user_input)], n)
    result = search(query)
    return result


def example_relationship(n=10):
    '''
    This function returns examples of relationships in the graph based on user selected relationship type.
    '''

    # Get user to specify relationship type for example
    print("Which relationship type do you want to see examples of?")
    relationships = get_rel_types()
    idx_to_rel = {idx: rel for idx, rel in enumerate(relationships)}
    for idx, rel in idx_to_rel.items():
        print(f"{idx}: {rel}")

    user_input = input("Enter a number: ")
    while True:
        valid_input = int(user_input) in idx_to_rel.keys()
        if valid_input:
            break
        else:
            print("Invalid input")
            user_input = input("Enter a number: ")

    # Make query
    query = '''MATCH (n1)-[r:`%s`]->(n2)
    RETURN n1, r, n2 LIMIT %s
    ''' % (idx_to_rel[int(user_input)], n)
    result = search(query)
    return result


def interactive():
    interactive_options = {'q': ('Query', 'Query the Neo4j Database with your own Cypher command'),
                           'p': ('Node Properties', 'Get the node schema of the graph'),
                           'r': ('Relationships', 'Get the relationship types in the graph'),
                           'u': ('Unique relationships', 'Get the unique relationships and the node types it connects'),
                           'en': ('Example node', 'Get examples of nodes in the graph based on node type'),
                           'er': ('Example relationship', 'Get examples of relationships in the graph based on '
                                                          'relationship type')
                           }

    verify_connection()

    while True:
        # Get user input
        user_input = input(get_user_prompt(interactive_options))

        if user_input == 'q':
            print("Query.")
            query()
        elif user_input == 'p':
            print("Properties.")
            result = get_node_type_properties()
            for p, v in result.items():
                print(p, "\tNode properties: ", v)
            print("Total number of node types: ", len(result), "\n")
        elif user_input == 'r':
            print("Relationships.")
            result = get_rel_types()
            for r in result:
                print(r)
            print("Total number of relationships: ", len(result), "\n")
        elif user_input == 'u':
            print("Unique relationships.")
            result = get_uniq_relation_pairs()
            for n1, r, n2 in result:
                print(n1, r, n2)
            print("Total number of unique relationships: ", len(result), "\n")
        elif user_input == 'en':
            print("Example node.")
            result = example_node()
            print(result)
        elif user_input == 'er':
            print("Example relationship.")
            result = example_relationship()
            print(result)


if __name__ == "__main__":
    interactive()
