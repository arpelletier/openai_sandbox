# NOTE: This file uses LangChain capabilites in conversing with the user
from openai import OpenAI
import sys
import os
import re
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from neo4j_driver import Driver

sys.path.append('../')
from config import OPENAI_KEY
client = OpenAI(api_key=OPENAI_KEY)

NODES = ...
EDGES = ...

def get_log_file(directory):
    """
    Find the directory for the logs and return the relevant 
    file that needs to be written to.
    """
    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Find the next available log file
        log_file = None
        i = 0
        while True:
            log_file = os.path.join(directory, f"log_{i}.txt")
            if not os.path.exists(log_file):
                break
            i += 1

        return log_file
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def write_to_log(log_file, text):
    """Using a log file, write text to it."""
    try:
        with open(log_file, 'a') as file:
            file.write(text + '\n')
    except Exception as e:
        print(f"An error occured: {str(e)}")

# TODO: Store in txt
NODE_TYPES = """
MeSH_Compound,['name']
Entrez,['name']
UniProt,['name']
Reactome_Reaction,['name']
MeSH_Tree_Disease,['name']
MeSH_Disease,['name']
Reactome_Pathway,['name']
MeSH_Anatomy,['name']
cellular_component,['name']
molecular_function,['name']
MeSH_Tree_Anatomy,['name']
ATC,['name']
DrugBank_Compound,['name']
KEGG_Pathway,['name']
biological_process,['name']
"""
nodes = NODE_TYPES.split(',')
NODE_LABELS = [node.replace('\n', '').replace('[\'name\']', '') for node in nodes][:-1]
# TODO: Store in txt
RELATIONSHIP_TYPES = """
"isa"
"`-increases->`"
"`-decreases->`"
"`-interacts_with->`"
"`-output->`"
"`-underexpressed_in->`"
"involved_in"
"`-overexpressed_in->`"
"located_in"
"`-may_participate_in->`"
"enables"
"-associated_with-"
"is_active_in"
"part_of"
"-diseases_share_variants-"
"decreases"
"`-transcription_factor_targets->`"
"-is-"
"`-pathway_is_parent_of->`"
"-ppi-"
"`-catalystActivity->`"
"increases"
"`-participates_in->`"
"`-involved_in->`"
"`-encodes->`"
"-diseases_share_genes-"
"`-input->`"
"`-negatively_regulates->`"
"`-entityFunctionalStatus->`"
"`-regulates->`"
"`-treats->`"
"`-associated_with->`"
"`-regulatedBy->`"
"colocalizes_with"
"`-positively_regulates->`"
"`-drug_participates_in->`"
"`-inhibits_downstream_inflammation_cascades->`"
"`-inhibitory_allosteric_modulator->`"
"acts_upstream_of"
"`-affects->`"
"NOT|involved_in"
"`-unknown->`"
"`-disease_involves->`"
"`-negative_modulator->`"
"-not_associated_with-"
"`-drug_participates_in_pathway->`"
"`-potentiator->`"
"`-suppressor->`"
"`-activator->`"
"-drug_uses_protein_as_enzymes-"
"NOT|located_in"
"`-drug_targets_protein->`"
"`-stimulator->`"
"`-inhibitor->`"
"acts_upstream_of_or_within"
"`-nucleotide_exchange_blocker->`"
"`-agonist->`"
"`-antagonist->`"
"`-partial_agonist->`"
"`-cofactor->`"
"-drug_uses_protein_as_transporters-"
"`-stabilization->`"
"`-binder->`"
"`-inducer->`"
"`-ligand->`"
"`-modulator->`"
"-drug_uses_protein_as_carriers-"
"`-component_of->`"
"`-chelator->`"
"`-regulator->`"
"`-chaperone->`"
"`-inactivator->`"
"`-neutralizer->`"
"`-cleavage->`"
"NOT|part_of"
"NOT|enables"
"`-multitarget->`"
"`-oxidizer->`"
"contributes_to"
"NOT|contributes_to"
"NOT|acts_upstream_of_or_within_negative_effect"
"acts_upstream_of_or_within_positive_effect"
"`-antisense_oligonucleotide->`"
"`-downregulator->`"
"NOT|colocalizes_with"
"`-inverse_agonist->`"
"`-partial_antagonist->`"
"`-translocation_inhibitor->`"
"`-blocker->`"
"acts_upstream_of_positive_effect"
"`-weak_inhibitor->`"
"`-antibody->`"
"`-inhibition_of_synthesis->`"
"`-binding->`"
"`-product_of->`"
"`-substrate->`"
"`-other/unknown->`"
"`-degradation->`"
"`-allosteric_modulator->`"
"`-positive_allosteric_modulator->`"
"NOT|acts_upstream_of_or_within"
"`-other->`"
"NOT|is_active_in"
"acts_upstream_of_or_within_negative_effect"
"acts_upstream_of_negative_effect"
"""

def extract_code(response: str):
    code_blocks = re.findall(r'```(.*?)```', response, re.DOTALL)
    # Combine code to be one block
    code = '\n'.join(code_blocks)
    return code

def get_relationships(cypher_code: str):
    driver = Driver()
    relationships = dict()

    # Gather all node labels
    node_label_pattern = r'\((\w+):(\w+)\)'
    node_labels = re.findall(node_label_pattern, cypher_code)
    node_types = set([node[1] for node in node_labels if node[1] in NODE_LABELS])

    # Now that you have the node types, you need to check the avalible relationships per node type
    for node_type in node_types:
        check_relationships_query = 'MATCH (n:{})-[r]->(m) RETURN DISTINCT type(r) AS relationship_type'.format(node_type)
        relation_types_list = driver.query_database(check_relationships_query)
        relationship_types = [relation['relationship_type'] for relation in relation_types_list]
        relationships[node_type] = relationship_types
    
    return relationships

class OpenAI_API():

    def __init__(self):
        # TODO: Find a way to add context without having to send "useless" queries
        self.conversation = ConversationChain(llm=ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_KEY))
        self.log_folder = os.path.join('../chat_log')
        self.driver = Driver()
        
    
    def add_context(self, debug=True):
        log_file = get_log_file(self.log_folder)
        # Document the node types and the node properties
        self.conversation.invoke("What are the node types in the neo4j graph? List a node label, then a comma, then a list of node properties.") 
        # Change the contents
        self.conversation.memory.chat_memory.messages[1].content = NODE_TYPES
        # Document in logs
        write_to_log(log_file, "What are the node types in the neo4j graph? List a node label, then a comma, then a list of node properties.\n" + self.conversation.memory.chat_memory.messages[1].content)
        
        # Document the relationships 
        self.conversation.invoke("What are the relationships? List the name of the relationship exactly as it appears in quotes and seperate with new lines.") 
        # Change the contents
        self.conversation.memory.chat_memory.messages[3].content = RELATIONSHIP_TYPES
        # Document in logs
        write_to_log(log_file, "What are the relationships? List the name ofand seperate with new lines.\n" + self.conversation.memory.chat_memory.messages[3].content)
        
        if debug:
          print("SUCCESSFULLY ADDED CONTEXT...")
          print(self.conversation.memory)  

    
    def single_chat(self, summarize=False, init_query=''):
        # For a single chat, just write everything that occurs in a conversation in 1 log file
        log_file = get_log_file(self.log_folder)
        
        # Index at 5 since there were already previous queries to add context
        self.add_context(debug=False)
        conv_index = 5

        # Determine if query needs to be corrected
        query_correction = False

        # Save the original query for later
        original_query = ''

        # Begin conversation
        for i in range(9999):
            if init_query != '' and i == 0:
                user_input = init_query
            else:
                # Collect user input
                user_input = input("User Input: ")
                if not query_correction:
                    original_query = user_input

            # Let the user ask a question
            self.conversation.invoke(user_input) 
            llm_response = self.conversation.memory.chat_memory.messages[conv_index].content
            conv_index += 2

            extracted_code = extract_code(llm_response)
            
            ################################################################################
            # FOR DEBUGGING PURPOSES
            print('CONVERSATION MEMORY:\n*************')
            for j in range(len(self.conversation.memory.chat_memory.messages)):
                print('INDEX: {}\t ITERATION: {}'.format(j, i))
                print(self.conversation.memory.chat_memory.messages[j].content)
                print('*************')
            print('------------------------------------------------------------------------------------------\n')  
            ################################################################################  
            
            ################################################################################
            # QUERY CHECKING
            # NOTE: WILL PUT INTO A FUNCTION LATER
            print('QUERY CHECKING\n*************')
            query_code, query_msg = self.driver.check_query(extracted_code)
            
            if query_code == -1:
                # Query Code -1 means that there was an exception
                # This likely means that there was some syntax error
                # In this case, we can reprompt the LLM and send in more context letting it know about the exception
                
                # Report the error to the user
                print('The query generated by the LLM resulted in an exception.')
                print(query_msg)
                print('Reprompting the LLM...')
                
                # Reprompt the LLM
                updated_input = "The query returned an exception: {}. Return another cypher query.".format(query_msg)

                # Reask the LLM
                self.conversation.invoke(updated_input) 
                updated_llm_response = self.conversation.memory.chat_memory.messages[conv_index].content
                conv_index += 2
                print('UPDATED LLM RESPONSE')
                print(updated_llm_response)

                extracted_code = extract_code(updated_llm_response)
                _, query_msg = self.driver.check_query(extracted_code)
                query_correction = True

            elif query_code == -2:
                # Report the error to the user
                print('The query generated by the LLM did not return any results.')
                print('Reprompting the LLM...')

                # Get the relationships in the original code 
                relations = get_relationships(extracted_code)

                # Send in an updated message to the LLM that makes sure that all rules are followed.
                updated_input = """
                The query did not return any results.
                Make another query. Make sure that all names have the correct identifier. 
                For example, names should be listed as \'UniProt:Q7L576\' or \'MeSH_Compound:C554777\'.
                Here is a dictionary of relationships each node type can have. Make sure this list is adhered to: {}
                """.format(relations)

                # Reask the LLM
                self.conversation.invoke(updated_input) 
                updated_llm_response = self.conversation.memory.chat_memory.messages[conv_index].content
                conv_index += 2
                print('UPDATED LLM RESPONSE')
                print(updated_llm_response)

                extracted_code = extract_code(updated_llm_response)
                _, query_msg = self.driver.check_query(extracted_code)
                query_correction = True

            # Once you already corrected the query, you can check if the question is any good
            # Cite the most recent query as evidence
            updated_input = """
            Here is the response of the most recent cypher query: {}.
            Based on the response, judge the original question: {}
            Cite the generated cypher query as evidence.
            """.format(query_msg, original_query)

            # Reprompt
            print('User:', updated_input)
            self.conversation.invoke(updated_input) 
            updated_llm_response = self.conversation.memory.chat_memory.messages[conv_index].content
            conv_index += 2
            print(updated_llm_response)


            # Save responses
            write_to_log(log_file, "User query: " + user_input)
            write_to_log(log_file, llm_response)
            write_to_log(log_file, "---------------------------------------------------------------------------")

if __name__ == "__main__":
    x = OpenAI_API()
    x.single_chat()




