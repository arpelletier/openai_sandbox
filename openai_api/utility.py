import re

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