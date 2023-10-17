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


def clear_neo4j():
	'''
	source: https://stackoverflow.com/questions/23310114/how-to-reset-clear-delete-neo4j-database
	'''
	print(get_node_type_properties())

	DELETE_RELS='''
		:auto MATCH ()-[r]->() 
		CALL { WITH r 
		DELETE r 
		} IN TRANSACTIONS OF 50000 ROWS;
		'''

	DELETE_NODES='''
		:auto MATCH (n) 
		CALL { WITH n 
		DETACH DELETE n 
		} IN TRANSACTIONS OF 50000 ROWS;
		'''

	search(DELETE_RELS)
	search(DELETE_NODES)

	return "Deleted" + get_node_type_properties() 



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

def query():

	test_input = 'MATCH (tom:Person {name: "Tom Hanks"})-[:ACTED_IN]->(tomHanksMovies)\nRETURN tom,tomHanksMovies'
	return search(test_input)


def populate_temp():
	'''
	This function populates the KG with dummy relations and nodes
	'''

	# TODO Step 2: Load from a triple file

	return "Test"

def interactive():
	while True:
		# Get user input
		user_input = input("Query (q); Delete (d); Populate (p)")

		if user_input == 'q':
			print("Query.")
			result = query()
		elif user_input == 'd':
			print("Delete.")
			result = clear_neo4j()
		elif user_input == 'p':
			print("Populate.")
			result = populate_temp()
			


		print(result)






if __name__ == "__main__":
    interactive()
	#print(get_node_type_properties())
