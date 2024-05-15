import sys
sys.path.append('../')
from neo4j import GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

URI = NEO4J_URI
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

class Driver:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, database="neo4j"):
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
    
    def check_query(self, query: str):
        query_result = self.query_database(query)
        if isinstance(query_result, Exception):
            return -1, 'AN EXCEPTION OCCURED FROM QUERY: {}'.format(query_result)
        if query == []:
            return -2, 'No results found'
        else:
            return 0, 'These are the results of the query as a list: {}'.format(query_result)
            
def testing():
    query = """MATCH p = (n:SMPDB_Pathway {name: \'SMPDB_Pathway:SMP0019503\'})-[]-() RETURN p"""
    print(query)
    driver = Driver()
    driver.verify_connectivity()
    result = driver.query_database(query)
    print('QUERY RESULT:', result)
    driver.close()

if __name__ == '__main__':
    testing()
