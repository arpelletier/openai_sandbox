import re
import json
from neo4j_driver import Driver
from tqdm import tqdm
import os
import ijson
import time

NODE_FEATURES_PATH = "data/node_features.json"

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

# def find_nodes(nodes: list):
#     """
#     OLD. Used to find nodes from the smaller json node features
#     which corresponded to the KG subset.
#     """
#     node_dict = dict()
#     jdata = json.loads(open ('data/node_features.json').read())
#     # import pdb; pdb.set_trace()
#     try:
#         for node in set(nodes):
#             node_dict[node] = jdata[node]['name']
#         return node_dict
#     except:
#         return {}

# Test to see what types of nodes there are
def find_node_names(max_nodes_to_return=5, returned_nodes=['MeSH_Compound:C568512', 'molecular_function:0140775', 'MeSH_Tree_Disease:C17.800.893.592.450.200']):
    node_names = dict()
    # Check all node types
    for i, returned_node in enumerate(returned_nodes):
        if i == max_nodes_to_return:
            break
        with open(NODE_FEATURES_PATH) as f:
            # Set up iterator for a single node
            nodes_objects = ijson.items(f, returned_node)
            node_object = next(nodes_objects)
            # If there is a names attribute, then use those
            if 'names' in node_object.keys():
                node_names[returned_node] = node_object['names']
            else:
                node_names[returned_node] = ["No known names"]
            continue
    print("returned_nodes:", returned_nodes)
    print("max_nodes_to_return:", max_nodes_to_return)
    return node_names

def extract_results(query: str, is_json=False):
    # Initalize the driver
    driver = Driver()
    nodes = driver.query_database(query)

    # Set up the regex
    node_names = ["MeSH_Compound", "Entrez", "UniProt", "Reactome_Reaction", "MeSH_Tree_Disease", "MeSH_Disease",
                  "Reactome_Pathway", "MeSH_Anatomy", "cellular_component", "molecular_function", "MeSH_Tree_Anatomy",
                  "ATC", "DrugBank_Compound", "KEGG_Pathway", "biological_process"]
    node_finder_pattern = r'(\b(?:' + '|'.join(map(re.escape, node_names)) + r')\S*)'

    # Check if json returned an invalid or valid object
    if is_json:
        try:
            string_json_nodes = json.dumps(nodes)
        except:
            return {}
        matches = re.compile(node_finder_pattern).findall(string_json_nodes)
    else:
        matches = re.compile(node_finder_pattern).findall(str(nodes))

    # Clean up results
    replace_chars = ['{', '}', '\'', '\"', '[', ']', ',', '(', ')']
    print('MATCHES BEFORE CLEAN UP:', matches)
    for i, match in enumerate(matches):
        print(match)
        for char in replace_chars:
            match = match.replace(char, "")
        matches[i] = match
    # Take set
    print('MATCHES:', matches)

    return find_node_names(returned_nodes=list(set(matches)))

def test_0():
    driver = Driver()
    query = "MATCH (d:DrugBank_Compound)-[:`-treats->`]->(disease) WHERE disease.name IN ['Entrez:202333', 'MeSH_Tree_Disease:C23.550.513.355.750', 'MeSH_Disease:D002312'] RETURN d.name AS DrugName LIMIT 30"
    results = driver.check_query(query)
    extracted_results = extract_results(results)
    print(extracted_results)

def test_1():
    response = """The hypothesis that Ketamine (MeSH_Compound:D007649) can be used to treat Ventricular Tachyarrhythmia (MeSH_Disease:D017180) can be explored further based on the query results from the biomedical knowledge graph. The specific query used was:
    MATCH (k:MeSH_Compound {name: 'MeSH_Compound:D007649'})-[:`-agonist->`]->(p:UniProt)
    RETURN p.name
    The results returned from this query were:
    [{'p.name': 'UniProt:P14416'}, {'p.name': 'UniProt:P41145'}]
    This indicates that Ketamine acts as an agonist to the proteins associated with the UniProt identifiers P14416 and P41145.
    UniProt:P14416 corresponds to the NMDA receptor subunit NR2B, which is part of the NMDA receptor complex involved in synaptic plasticity and memory function. UniProt:P41145 corresponds to the serotonin receptor 5-HT2A, which is involved in various neurological processes."""
    print(extract_results(response))

def test_2():
    query = """MATCH gamma = (k:MeSH_Compound {name: 'MeSH_Compound:D007649'}), (v:MeSH_Disease {name: 'MeSH_Disease:D017180'})
    MATCH (k)-[:`-treats->`]->(v)
    RETURN gamma
    """
    print(extract_results(query))

def test_3():
    matches = ['MeSH_Compound:D007649"},', 'MeSH_Disease:D017180"}],', 'MeSH_Compound:D007649"},', 'MeSH_Disease:D017180"}],', 'MeSH_Compound:D007649"},', 'MeSH_Disease:D017180"}],', 'MeSH_Compound:D007649"},', 'MeSH_Disease:D017180"}],']
    replace_chars = ['{', '}', '\'', '\"', '[', ']', ',']
    print('MATCHES BEFORE CLEAN UP:', matches)
    for i, match in enumerate(matches):
        print(match)
        print('*******')
        for char in replace_chars:
            print('REPLACE CHAR {}'.format(char))
            print("Before replace:", match)
            match = match.replace(char, "")
            print("After replace:", match)
        matches[i] = match
    print('MATCHES:', matches)

def test_4():
    return(list(set(['UniProt:P14416', 'UniProt:P41145', 'UniProt:P14416', 'UniProt:P14416', 'UniProt:P14416', 'UniProt:P41145', 'UniProt:P41145', 'UniProt:P41145'])))

if __name__ == "__main__":
    test_0()

