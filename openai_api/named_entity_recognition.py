import spacy
import sys
sys.path.append("..")
from config import MESH_ID_CONFIG
from scispacy.linking import EntityLinker
import json

class SpacyNER:
    def __init__(self):
        self.disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
        self.scientific_entity_nlp = spacy.load("en_ner_bionlp13cg_md")
        self.pos_nlp = spacy.load("en_core_web_sm")
        self.graph_nodes = json.loads(open('data/node_records.json', "r").read())

    def disease_ner(self, text: str):
        # disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
        document = self.disease_ner_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]

    def scientific_entity_ner(self, text: str):
        # disease_ner_nlp = spacy.load("en_ner_bionlp13cg_md")
        document = self.scientific_entity_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]

    def part_of_speech_tags(self, text: str):
        # pos_nlp = spacy.load("en_core_web_sm")
        document = self.pos_nlp(text)
        return [(token.text, token.pos_) for token in document]

    def show_entities(self, text: str):
        # TODO: FIX DUE TO CHANGE IN get_entities()
        disease_ner_results, scientific_entity_ner_results, pos_results, mesh_ids = self.get_entities(text)

        print("DISEASES: {}".format(disease_ner_results))
        print("OTHER ENTITIES: {}".format(scientific_entity_ner_results))
        print("PARTS OF SPEECH: {}".format(pos_results))
        print("MESH IDS: {}".format(mesh_ids))

    def get_mesh_ids(self, text: str):
        """Return mesh ids for named entites."""
        model = self.disease_ner_nlp
        model.add_pipe("scispacy_linker", config=MESH_ID_CONFIG)
        linker = model.get_pipe("scispacy_linker")

        # Find the knowledge base entities
        res = {}
        doc = model(text)
        for e in doc.ents:
            if e._.kb_ents:
                cui = e._.kb_ents[0][0]
                # print(e, cui)
                if e not in res:
                    res[e] = []
                res[e].append(cui)
        return res

    def get_entities(self, text: str):
        '''
        Returns disease and other scientific entity terms 
        '''
        # NOTE: Removed POS (not sure about usage) and mesh_id (not correct indexes)
        disease_ner_results = self.disease_ner(text)
        scientific_entity_ner_results = self.scientific_entity_ner(text)
        # pos_results = self.part_of_speech_tags(text)
        # mesh_ids = self.get_mesh_ids(text)

        return disease_ner_results, scientific_entity_ner_results

    def check_json(self, keywords):
        # Save all node types
        node_types = ['ATC', 'MeSH_Disease', 'biological_process', 'molecular_function', 'MeSH_Compound', 
                      'DrugBank_Compound', 'MeSH_Anatomy', 'KEGG_Pathway', 'MeSH_Tree_Disease', 'Reactome_Reaction', 
                      'MeSH_Tree_Anatomy', 'Reactome_Pathway', 'cellular_component', 'Entrez', 'UniProt']
        
        # Loop through all keywords
        for keyword in keywords:
            # Check all node types for each of the
            for node in node_types:
                # The keyword will have to have a specific prefix
                check_word = "{}:{}".format(node, keyword)
                # Make note that the keyword was found 
                if check_word in self.graph_nodes:
                    self.found_nodes.append(keyword)
        






if __name__ == "__main__":
    ner = SpacyNER()
    ner.check_json(keyword='Q86XR7')
    # prompt = "What does Pramipexole do?"

    # ner = SpacyNER()
    # ner.show_entities(prompt)
