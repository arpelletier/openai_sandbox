import os
import openai
from utils.utils import get_project_root
from NER.spacy_ner import SpacyNER
from utils.logger import get_log_file, write_to_log  # Import the logger functions
from openai_api.openai_client import call_openai_api
from neo4j_api.neo4j_api import Neo4j_API

def ner(input):
    """
    Where we would do NER on the next input.
    """
    print("Named Entity Recognition module:")

    ner = SpacyNER()
    disease_ner_results, scientific_entity_ner_results, pos_results, mesh_ids = ner.get_entities(input)

    # Look for mesh ids
    if mesh_ids:
        print("MESH IDS: {}".format(mesh_ids))
        disease_entities = [d.text for d in mesh_ids.keys()]

        # Get the mesh ids
        mesh_list = [mesh_ids[entity] for entity in mesh_ids.keys()]

        # Identify non-disease entities
        non_disease_entities = [entity for entity, e_type in scientific_entity_ner_results if
                                entity not in disease_entities]
        for entity, e_type in pos_results:
            if e_type == 'NOUN':
                in_diseases = False
                for d in disease_entities:
                    if entity in d:
                        in_diseases = True
                if not in_diseases:
                    non_disease_entities += [entity]

        relationships = []
        for entity, e_type in pos_results:

            if e_type == 'VERB':
                relationships += [entity]

    print("Non disease entities: {}".format(non_disease_entities))
    print("Relationships: {}".format(relationships))

    return mesh_ids, non_disease_entities, relationships


def kg(ner_results):
    """
    This function identifies relevant nodes in the knowledge graph
    """

    mesh_ids, non_disease_entities, relationships = ner_results

    # Connect to the Neo4j API
    neo4j_api = Neo4j_API()

    # Check the MeSH terms are in the graph if any
    for mesh_id in mesh_ids:
        mesh_query = '''
        MATCH (disease:MeSH_Disease {name: 'MeSH_Disease:%s'})
        '''
        result = neo4j_api.search(mesh_query)

        if not result:
            print("Mesh id {} not in graph".format(mesh_id))

    # Check the non-disease entities are in the graph if any
    for entity in non_disease_entities:
        '''
        TODO Joseph
        - Replace 'Entity' with the Node Type identified from Neo4j API
            e.g., neo4j_api.get_node_type_properties() -> find the closest match. Maybe ask LLM to identify best match?
        - After creating the query, query the KG see if the node exists (if it's a class-based node like 'drug',
          then get a few examples? Otherwise if it's a specific drug with an ID, check it exists.
        '''
        # entity_query = '''
        # MATCH (entity:Entity {name: '%s'})
        # '''
        # result = neo4j_api.search(entity_query)
        #
        # if not result:
        #     print("Entity {} not in graph".format(entity))
        temp = 'drug' # How to find a generalized entity type? Check node types to find a semantic match?
        print("Not yet implemented")

    # Check the relationships are in the graph if any
    for rel in relationships:
        '''
        TODO Joseph
        - Similar to above, but use neo4j_api.get_rel_types() to find the closest match.
        - To consider, how do we know which node types the relationships needs? This means we have to look at the 
          original query, in the NER step and identify head and tail of the relationship... Then we can use the
          neo4j_api.get_uniq_relation_pairs() to find the closest match. 
        '''
        # rel_query = '''
        # MATCH ()-[r:%s]->()
        # '''
        # result = neo4j_api.search(rel_query)
        #
        # if not result:
        #     print("Relationship {} not in graph".format(rel))
        temp = 'treats' # Check relationship types to find a semantic match?
        print("Not yet implemented")


def start_chat(log_file=None):
    while True:
        # Get user input
        # user_input = input("User: ")
        user_input = "What drugs treat lung cancer?"

        # Identify entities
        ner_results = ner(user_input)

        # Identifies relevant nodes in the knowledge graph
        kg_results = kg(ner_results)

        # Send to Open AI API
        # response = call_openai_api(user_input)

        if log_file:
            write_to_log(log_file, "User: " + user_input)
            write_to_log(log_file, response)


if __name__ == "__main__":
    log_folder = os.path.join(get_project_root(), 'chat_log')
    log_file = get_log_file(log_folder)

    start_chat(log_file=log_file)
