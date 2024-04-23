import sys
sys.path.append('../')
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

URI = NEO4J_URI
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

class Driver:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()
    
    def verify_connectivity(self):
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            try:
                driver.verify_connectivity()
                return True
            except:
                return False

    def query_database(self, query: str):
        with self.driver.session():
            try:
                result = self.driver.execute_query(query)
                return [res.data() for res in result.records]
            except (DriverError, Neo4jError) as Exception:
                return Exception
            
def testing():
    query = """MATCH (n:MeSH_Tree_Anatomy) RETURN n LIMIT 25"""
    driver = Driver(URI, NEO4J_USER, NEO4J_PASSWORD)
    result = driver.query_database(query)
    print('QUERY RESULT:', result)
    driver.close()

if __name__ == '__main__':
    testing()
