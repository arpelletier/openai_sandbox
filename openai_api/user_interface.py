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

class Interface():
    def __init__(self):
        self.llm_client = OpenAI_API()
        self.ner = NamedEntityRecognition()
        self.protein_utility = Protein_Utility()

    def chat(self):
        # Define user input and context
        user_input = input("User: ")
        context = self.ner.get_context(user_input)

        '''
        Check initial query
            If the query returns something, then immediately send it to the user
            If the query returns an exception, then return the exception to LLM 
            If the query returns nothing, still tell the LLM the issue but ask to try again
                Give it some reiminders like the namespace ID has to be right before
        '''
        
        # Define example
        example_node = "MATCH (p1:Entrez {name: 'Entrez:1756'})"
        llm_context = """
        Write a query in cypher to answer the query \"{}\". 
        Here is a dictionary where the key corresponds to a possible enttiy in the question and the values correspond to node names in the graph: {}
        Here is additional context for the query containing the node names. 
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
