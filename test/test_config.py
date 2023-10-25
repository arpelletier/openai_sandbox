# test_config.py tests the functionality for config.py

import unittest
import os
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_KEY
from neo4j import GraphDatabase
from utils.utils import get_project_root
from openai_api.openai_client import call_openai_api


class TestConfig(unittest.TestCase):

    def test_neo4j_config(self):
        self.assertIsNotNone(NEO4J_URI, "NEO4J_URI should not be None")
        self.assertIsNotNone(NEO4J_USER, "NEO4J_USER should not be None")
        self.assertIsNotNone(NEO4J_PASSWORD, "NEO4J_PASSWORD should not be None")

        print("NEO4J_URI:", NEO4J_URI)
        print("NEO4J_USER:", NEO4J_USER)
        print("NEO4J_PASSWORD:", NEO4J_PASSWORD)

    def test_openai_config(self):
        self.assertIsNotNone(OPENAI_KEY, "OPENAI_KEY should not be None")

        print("OPENAI_KEY:", OPENAI_KEY)

    def test_neo4j_connection(self):
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 AS x")
            record = result.single()
            self.assertEqual(record["x"], 1)

            driver.close()

        print("Neo4j connection successful\n")

    def test_openai_api_call(self):
        user_input = "Test user input"
        response = call_openai_api(user_input)
        self.assertIsNotNone(response, "OpenAI API response should not be None")

        print(user_input)
        print(response)
        print("OpenAI API call successful\n")


if __name__ == '__main__':

    loader = unittest.TestLoader()

    # Define test order
    test_order = [
        'test_neo4j_config',
        'test_openai_config',
        'test_neo4j_connection',
        'test_openai_api_call',
    ]

    # Run each test individually in order TODO doesn't execute in order...
    for test_name in test_order:
        suite = loader.loadTestsFromName(f"{TestConfig.__name__}.{test_name}")
        unittest.TextTestRunner(verbosity=2).run(suite)