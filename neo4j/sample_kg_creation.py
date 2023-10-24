'''
Author: Joseph Ramirez
Created: 10/23/23 11:00 PM
'''
import pandas as pd
from neo4j import GraphDatabase, RoutingControl

def clear_graph(session, debug=True):
    '''
    This function deletes all nodes and edges in the graph.
    '''
    
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    session.run(query)
    
    if debug:
        count_nodes_and_relationships(session, debug=True)
    

def count_nodes_and_relationships(session, debug=True):
    '''
    This function counts the number of nodes and edges in the graph.
    '''
    # Count nodes
    node_query = "MATCH (n) RETURN COUNT(n) AS nodeCount"
    nodes = session.run(node_query).single()["nodeCount"]

    # Count relationships
    relationship_query = "MATCH ()-->() RETURN COUNT(*) AS relationshipCount"
    relationships = session.run(relationship_query).single()["relationshipCount"]
    
    if debug:
        print(f"Number of nodes: {nodes}")
        print(f"Number of relationships: {relationships}")

    return nodes, relationships


def create_node(session, node_name, node_type):
    '''
    This function creates a new node with node_name and type node_type.
    '''
    query = """
    CREATE (n:%s {name:"%s"})
    RETURN n
    """%(node_type,":".join([node_type,node_name]))
    
    session.run(query)
    
    
def create_relationship(session, entity_1, entity_2, relation):
    '''
    This function creates a new relationship between entity_1 and entity_2.
    '''
    e1_type = entity_1.split(":")[0]
    e2_type = entity_2.split(":")[0]
    
    query = """
    MATCH (e1:%s {name: "%s"})
    MATCH (e2:%s {name: "%s"})
    WHERE e1 IS NOT NULL AND e2 IS NOT NULL
    MERGE (e1)-[:`%s`]->(e2)
    """ %(e1_type,entity_1,e2_type,entity_2,relation)
    result = session.run(query)
    
    # Consume the result to get the query summary
    summary = result.consume()
    
    # Check if the relationship was created
    if summary.counters.relationships_created == 0:
        print("Warning: One or both persons do not exist in the graph.")

def get_schema(driver):
    return driver.execute_query("call db.schema.nodeTypeProperties", database_="neo4j", routing_=RoutingControl.READ)

# Class handling the database connection
class Neo4jConnector:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()        


# Load Know2BIO Data
print("Loading sample data")

input_file = 'sample_data.txt'
df = pd.read_csv(input_file,sep="\t",header=None)
df.columns=['h','r','t']

nodes = set(df['h']).union(set(df['t']))
uniq_edges = set(df['r'])
relationships = list(zip(df['h'],df['r'],df['t']))

def create_graph(session):
    # Create nodes
    print("Creating nodes")
    count = 0
    for node in nodes:
        node_type,node_name = node.split(":")
        create_node(session, node_name, node_type)
        count += 1
        print(f'Nodes completed: %d out of %d'%(count,len(nodes)), end='\r', flush=True)
    print("%d nodes created.                        "%count)    
    
    # Create relationships
    print("Creating relationships")
    count = 0
    for h,r,t in relationships:
        create_relationship(session, h, t, r)
        count += 1
        print(f'Relationships completed: %d out of %d'%(count,len(relationships)), end='\r', flush=True)
    print("%d relationships created.                "%count)  
    
    # Print summary
    node_count, relationship_count = count_nodes_and_relationships(session)



neo4j_uri = "neo4j+s://d1751857.databases.neo4j.io"  # The default URI for Neo4j
neo4j_user = "neo4j"
neo4j_password = "Nwb27DK-3SuiqTAaW01VjVKRN_mnEgDLqQDVpPncVAI"

connector = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)

with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
    session = driver.session()
    print(get_schema(driver))
    






# with connector._driver.session() as session:
#     print("In the with statement")
#     count_nodes_and_relationships(session)
    # # Clear graph
    # print("Clearing Graph")
    # clear_graph(session, debug=False)
    
    # # Create nodes
    # print("Creating nodes")
    # count = 0
    # for node in nodes:
    #     node_type,node_name = node.split(":")
    #     create_node(session, node_name,node_type)
    #     count += 1
    #     print(f'Nodes completed: %d out of %d'%(count,len(nodes)), end='\r', flush=True)
    # print("%d nodes created.                        "%count)    
    
    # # Create relationships
    # print("Creating relationships")
    # count = 0
    # for h,r,t in relationships:
    #     create_relationship(session, h, t, r)
    #     count += 1
    #     print(f'Relationships completed: %d out of %d'%(count,len(relationships)), end='\r', flush=True)
    # print("%d relationships created.                "%count)  
    
    # # Print summary
    # node_count, relationship_count = count_nodes_and_relationships(session)

# from neo4j import GraphDatabase

# # Define a function to create the graph
# def create_graph(file_path, uri, user, password):
#     # Connect to the Neo4j database
#     driver = GraphDatabase.driver(uri, auth=(user, password))

#     # Open the text file and process each line
#     with open(file_path, 'r') as file:
#         for line in file:
#             parts = line.strip().split('\t')
#             if len(parts) == 3:
#                 node1 = parts[0]
#                 relationship = parts[1]
#                 node2 = parts[2]

#                 # Create a transaction to add nodes and relationships to the graph
#                 with driver.session() as session:
#                     session.write_transaction(add_nodes_and_relationships, node1, relationship, node2)

#     # Close the Neo4j driver
#     driver.close()

# # Define a function to add nodes and relationships
# def add_nodes_and_relationships(tx, node1, relationship, node2):
#     query = (
#         f"MERGE (n1:Node {{name: '{node1}'}}) "
#         f"MERGE (n2:Node {{name: '{node2}'}}) "
#         f"MERGE (n1)-[:{relationship}]->(n2)"
#     )
#     tx.run(query)

# if __name__ == "__main__":
#     file_path = 'your_text_file.txt'
#     neo4j_uri = 'bolt://localhost:7687'  # Replace with your Neo4j server URI
#     neo4j_user = 'your_username'  # Replace with your Neo4j username
#     neo4j_password = 'your_password'  # Replace with your Neo4j password

#     create_graph(file_path, neo4j_uri, neo4j_user, neo4j_password)
