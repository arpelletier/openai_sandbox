from openai_client_langchain import OpenAI_API
from named_entity_recognition import NamedEntityRecognition
from protein_utils import Protein_Utility
from neo4j_driver import Driver

class Interface():
    def __init__(self):
        self.llm_client = OpenAI_API()
        self.ner = NamedEntityRecognition()
        self.driver = Driver()
        self.protein_utility = Protein_Utility() # NOTE: idk if i need this maybe get rid of it

    def chat(self):
        # Define user input and context
        user_input = input("User: ")
        context = self.ner.get_context(user_input)
        
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
