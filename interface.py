import os
import openai
from utils.utils import get_project_root
from NER.spacy_ner import SpacyNER
from utils.logger import get_log_file, write_to_log  # Import the logger functions
from openai_api.openai_client import call_openai_api


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




def start_chat(log_file=None):
    while True:
        # Get user input
        # user_input = input("User: ")
        user_input = "What drugs treat lung cancer?"

        # Identify entities
        ner_results = ner(user_input)

        # Send to Open AI API
        # response = call_openai_api(user_input)

        if log_file:
            write_to_log(log_file, "User: " + user_input)
            write_to_log(log_file, response)


if __name__ == "__main__":
    log_folder = os.path.join(get_project_root(), 'chat_log')
    log_file = get_log_file(log_folder)

    start_chat(log_file=log_file)
