import os
import openai
from utils.utils import get_project_root
from NER.spacy_ner import SpacyNER
from utils.logger import get_log_file, write_to_log  # Import the logger functions
from openai_api.openai_client import call_openai_api
from neo4j_api.neo4j_api import Neo4j_API
from openai_api.chat_test import single_chat as gpt_response

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

    mesh_id_results = list()
    non_disease_ent_results = list()
    relationship_results = list()

    # Connect to the Neo4j API
    neo4j_api = Neo4j_API()

    # Check the MeSH terms are in the graph if any
    for mesh_id in mesh_ids:
        print(mesh_ids[mesh_id])
        mesh_query = "MATCH (n:MeSH_Disease {{name: 'MeSH_Disease:{}'}}) RETURN n LIMIT 25".format(mesh_ids[mesh_id][0])
        result = neo4j_api.search(mesh_query)
        mesh_id_results.append([mesh_ids[mesh_id][0], result])
    
    # Check the non-disease entities are in the graph if any
    node_types = neo4j_api.get_node_types()
    for entity in non_disease_entities:
        prompt = """Which of the following is {} most similar to in the following list: {}? 
        You may select an item even if it does not seem that similar, just be sure to pick one.
        Only list the terms seperated by commas with no additional information or descriptions.""".format(entity, node_types)
        prompt_response = gpt_response(prompt)
        non_disease_ent_results.append([entity, prompt_response])

    # Check the relationships are in the graph if any
    relationship_types = neo4j_api.get_rel_types()
    for rel in relationships:
        print()
        prompt = """Which of the following is {} most similar to in the following list: {}? 
        You may select an item even if it does not seem that similar, just be sure to pick one and 
        only list the terms seperated by commas with no additional information or descriptions.""".format(rel, relationship_types)
        prompt_response = gpt_response(prompt)
        relationship_results.append([rel, prompt_response])

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
    prompt = "Which pathways are most significant in p53 signaling in patients with a carcinoma?"
    kg(ner(prompt))

# if __name__ == "__main__":
#     text = """
#     What genes are most important in colon cancer and diabetes?
#     What drugs treat Crohn's disease?
#     List the medications someone with pneumonia may be prescribed.
#     Which pathways are most significant in p53 signaling in patients with breast cancer?
#     What are different treatment options for ADHD?
#     What are preventative measures for heart disease?
#     How does ibuprofen help with menstrual pain?
#     Explain what happens to neurons in patients with multiple sclerosis.
#     Is scoliosis curable?
#     How long are most treatments for lung cancer good for?
#     """

#     stripped_text = text.strip().split('\n')
#     single_texts = [i.strip() for i in stripped_text]
#     non_disease_entities = list()
#     relationships = list()

#     for st in single_texts:
#        ner_results = ner(st)
#        non_disease_entities.append(ner_results[1]) 
#        relationships.append(ner_results[2])

#     print("NON DISEASE ENTITIES")
#     print(non_disease_entities)

#     print("RELATIONSHIPS")
#     print(relationships)

    
    # neo4j_querier = Neo4j_API()
    # properties = neo4j_querier.get_node_type_properties()
    # print(properties)
    # log_folder = os.path.join(get_project_root(), 'chat_log')
    # log_file = get_log_file(log_folder)
    # start_chat(log_file=log_file)

"""
Spare notes
        '''
        TODO Joseph
        - Replace 'Entity' with the Node Type identified from Neo4j API
            e.g., neo4j_api.get_node_type_properties() -> find the closest match. Maybe ask LLM to identify best match?
        - After creating the query, query the KG see if the node exists (if it's a class-based node like 'drug',
          then get a few examples? Otherwise if it's a specific drug with an ID, check it exists.

        MY NOTES
        Do ner on the results (which is what is currently doing) and see the results that are most most similar to 
        '''

        '''
        TODO Joseph
        - Similar to above, but use neo4j_api.get_rel_types() to find the closest match.
        - To consider, how do we know which node types the relationships needs? This means we have to look at the 
          original query, in the NER step and identify head and tail of the relationship... Then we can use the
          neo4j_api.get_uniq_relation_pairs() to find the closest match. 
        '''
"""