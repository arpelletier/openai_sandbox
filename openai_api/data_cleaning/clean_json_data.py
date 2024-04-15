import sys
import json
sys.path.append("..")

"""
This file runs in order to add a NODE_TYPE variable to each entry.
DO NOT RERUN. This file only needs to be run once.
"""

JSON_FILE_PATH = '../data/node_features.json'

with open (JSON_FILE_PATH) as f:
    data = json.load(f)

    # Add a node type to each node
    for node in data:
        data[node]['NODE_TYPE'] = node.split(':')[0]

    with open (JSON_FILE_PATH, 'w') as updated_file: 
        # Write all data back to the json
        json.dump(data, updated_file)

print('Process Complete.')