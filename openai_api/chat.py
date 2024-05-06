import sys
import re
from openai import OpenAI
from neo4j_driver import Driver
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from named_entity_recognition import NamedEntityRecognition

# Save open AI key
sys.path.append('../')
from config import OPENAI_KEY

def get_node_and_edge_types(node_path='data/node_types.txt', edge_path='data/edge_types.txt'):
    node_types_path = node_path
    edge_types_path = edge_path

    node_types = ""
    edge_types = ""

    with open(node_types_path) as f:
        for node in f:
            node_types += f"\"{node.strip()}\";"
        node_types = node_types[:-1]       

    with open(edge_types_path) as f:
        for edge in f:
            edge_types += f"\"{edge.strip()}\","
        edge_types = edge_types[:-1]
    
    return node_types, edge_types

def read_query_examples(query_examples_path='data/query_examples.txt'):
    with open(query_examples_path, 'r') as f:
        query_examples = f.read()
        return query_examples

def extract_code(response: str):
    code_blocks = re.findall(r'```(.*?)```', response, re.DOTALL)
    # Combine code to be one block
    code = '\n'.join(code_blocks)
    return code

NODE_TYPES, EDGE_TYPES = get_node_and_edge_types()
QUERY_EXAMPLES = read_query_examples()

class Chat:
    def __init__(self, initial_question):
        # Save the inital question for downstream purposes
        self.inital_question = initial_question

        # Save an NER object to generate a context for the initial query
        self.ner = NamedEntityRecognition()

        # Initialize query builder, query evaluator and reasoner
        self.query_builder = ConversationChain(llm=ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_KEY))
        self.query_evaluator = ConversationChain(llm=ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_KEY))
        self.reasoner = ConversationChain(llm=ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_KEY))

        # Add contexts to each LLM agent
        self.qb_index = self.init_query_builder(debug=True)
        self.qe_index = self.init_query_evaluator()
        self.r_index = 1

    def init_query_builder(self, debug=False):
        # The intial context is composed the nodes and edges
        self.query_builder.invoke("What are the node types in the neo4j graph? List the name of the nodes exactly as it appears in quotes and seperate with commas.")
        self.query_builder.memory.chat_memory.messages[1].content = NODE_TYPES
        self.query_builder.invoke("What are the relationships? List the name of the relationship exactly as it appears in quotes and seperate with commas.") 
        self.query_builder.memory.chat_memory.messages[3].content = EDGE_TYPES

        # Acknowledge some of the rules that may be needed for formulating queries
        self.query_builder.invoke("What are some general rules for formulating queries?")
        self.query_builder.memory.chat_memory.messages[5].content = "All nodes have the \'name\' property. Node names are typically identifiers such as 'UniProt:P04004'. You must include a namespace identifier such as UniProt: before node names.\n" + QUERY_EXAMPLES

        if debug:
            print('PRINTING QUERY BUILDER MEMORY')
            print(self.query_builder.memory)
            print('Query Builder initialization completed.')
        
        return 7

    def init_query_evaluator(self):
        # Also provide the query evaluator with the relevant context
        self.query_evaluator.invoke("What are the node types in the neo4j graph? List the name of the nodes exactly as it appears in quotes and seperate with commas.")
        self.query_evaluator.memory.chat_memory.messages[1].content = NODE_TYPES
        self.query_evaluator.invoke("What are the relationships? List the name of the relationship exactly as it appears in quotes and seperate with commas.") 
        self.query_evaluator.memory.chat_memory.messages[3].content = EDGE_TYPES

        # Provide the query evaluator with examples
        self.query_evaluator.invoke("What are some examples of cypher queries for this graph?")
        self.query_evaluator.memory.chat_memory.messages[5].content = QUERY_EXAMPLES

        return 7
    
    def generate_initial_query_context(self):
        # Generate inital query context
        context = self.ner.get_context(self.inital_question)
        example_node = "MATCH (p1:Entrez {name: 'Entrez:1756'})"
        llm_context = """
        Write a query in cypher to answer the question \"{}\". 
        Here is a dictionary where the key corresponds to a possible named entities in the question and the values correspond to node names in the graph: {}
        Here is additional context for the query containing the node names. 
        For example, this would mean if the context included the tuple ('dystrophin', 'Entrez:1756'), then {} would find the node. 
        Avoid using the CONTAINS keyword.
        """.format(self.inital_question, context, example_node)
        return llm_context
    
    def generate_inital_reasoner_context(self):
        context = "Generate a "
        ...

    def conversation(self):
        # Save a driver instance for downstream query checking
        neo4j_driver = Driver()

        for i in range(9999):
            if i == 0:
                # Upon initally starting the conversation, ask the query builder to design a query
                initial_question = self.generate_initial_query_context()
                self.query_builder.invoke(initial_question)
                generated_query = extract_code(self.query_builder.memory.chat_memory.messages[self.qb_index].content)
                self.qb_index += 2
                # Have the query evaluator modify the query
                self.query_evaluator.invoke('Make sure the following query is correct syntactically and makes sense to answer the question {}. Modify if needed and otherwise return the original query.'.format(generated_query))
                modified_query = extract_code(self.query_evaluator.memory.chat_memory.messages[self.qe_index].content)
                self.qe_index += 2
            else:
                # In the else, either you are reprompting or you are still trying to 
                # get a query that can compile
                if query_code == -1:
                    self.query_builder.invoke(query_msg)
                else:
                    updated_input = input('User Input: ')
                    self.query_builder.invoke(updated_input)
                
                # In either case, you end up building a query and checking it
                generated_query = extract_code(self.query_builder.memory.chat_memory.messages[self.qb_index].content)
                self.qb_index += 2
                self.query_evaluator.invoke('Make sure the following query is correct syntactically and makes sense to answer the question {}. Modify if needed and otherwise return the original query.'.format(generated_query))
                modified_query = extract_code(self.query_evaluator.memory.chat_memory.messages[self.qe_index].content)
                self.qe_index += 2


            # After the query is checked, see if anything returns 
            if modified_query != "":
                query_code, query_msg = neo4j_driver.check_query(modified_query)
            else:
                query_code, query_msg = neo4j_driver.check_query(generated_query)
            
            if query_code == -1:
                # If the query code is -1, then there was an error
                # Restart the loop and go back to the top
                continue
            else:
                # If the query code is not -1, then you should be able to use the reasoner
                # Once the reasoner gives a response, reprompt
                reasoner_query = """
                Formulate a response based on your knowledge to this question: {}.
                I queried a biomedical knowledge graph with this query: {}.
                These were the results returned: {}
                Also cite the results of the query in your response.""".format(self.inital_question, modified_query, query_msg)
                self.reasoner.invoke(reasoner_query)
                message = self.reasoner.memory.chat_memory.messages[self.r_index].content
                self.r_index += 2

                # DEBUG
                print('QUERY BUILDER HISTORY')
                print(self.query_builder.memory)
                print('QUERY EVALUATOR HISTORY')
                print(self.query_evaluator.memory)
                print('ORIGINAL GENERATED QUERY')
                print(generated_query)
                print('MODIFIED QUERY')
                print(modified_query)
                # DEBUG

                print('REASONER MESSAGE')
                print(message)


        




        # first, send the question to the query builder
        # next, have the query reasoner modify the code 
        # After, get the code checked to see if there are any results
        # If code compiles, send to reasoner
            # After sending to reasoner, reprompt
        # If code does not compile, restart at step 1


if __name__ == '__main__':
    question = "How viable is this hypothesis: Mercuric Chloride interacts with Alpha-Synuclein and other proteins involved in protein misfolding and aggregation pathways, exacerbating neurotoxicity."
    chat = Chat(question)
    chat.conversation()