'''
1. Ask for user input 
2. Perform NER
    a. with NER results, see what hits the dictionary 
    b. if no exact match, re ask user for more context
3. Send the context to the llm and ask to generate a query
    - Here are the relevant terms in the graph: ___, ____, ___, ...
    - Now, make me a query to <original ask>
'''

'''
NOTE
Since the mesh ids may not be updated, I focused specifically on UniProt
'''

from openai_client_langchain import OpenAI_API
from named_entity_recognition import NamedEntityRecognition
from protein_utils import Protein_Utility
from rag_system import RAG

class Interface():
    def __init__(self):
        self.llm_client = OpenAI_API()
        # TODO: idk if these two belong here
        # Maybe keep these in another file/move them so their utility
        # is better delegated
        self.ner = NamedEntityRecognition()
        self.protein_utility = Protein_Utility()

    def process_ner_gene_products(self, ner_results: list):
        '''
        TODO: Might have to move this over to the protein utils class

        For the time being, only focus on processing proteins.
        Return a list of proteins that had findable aliases
        '''
        findable_protein_names = dict()
        not_findable_protein_names = set()

        for ner_result in ner_results:
            if ner_result[1] == 'GENE_OR_GENE_PRODUCT':
                # See if the protein name has a findable corresponding UniProt ID
                proteins = self.protein_utility.search_protein(ner_result[0])

                # Check if the protein name exists in the KG
                found_proteins = self.protein_utility.check_in_kg(proteins)

                # Document whether or not the protein is in the KG
                if found_proteins == []:
                    not_findable_protein_names.add(ner_result[0])
                else:
                    findable_protein_names[ner_result[0]] = found_proteins

        return findable_protein_names, not_findable_protein_names
    
    def process_ner_results(self, ner_results: list):
        '''
        For all NER results, check if there are any name matches in the nodes.
        syntrophin gamma 1
        '''
        for result in ner_results:
            ...

    def chat(self):
        # Define user input and context
        user_input = input("User: ")
        context = self.ner.generate_context(user_input)

        # Define example
        example_node = "MATCH (p1:Entrez {name: 'Entrez:1756'})"
        llm_context = """
        Write a query in cypher to answer the query \"{}\". 
        Here is additional context for the query containing the node names. 
        The first entry per tuple is a name and the second entry per tuple is the name of the node in the graph: {}.
        For example, this would mean if the context included the tuple ('dystrophin', 'Entrez:1756'), then  {} would find the node. 
        """.format(user_input, context, example_node)

        # Initiate conversation
        self.llm_client.single_chat(init_query=llm_context)
        return

def main():
    interface = Interface()
    interface.chat()

if __name__ == "__main__":
    main()
