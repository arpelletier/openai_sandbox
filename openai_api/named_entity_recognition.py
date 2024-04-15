import spacy
import sys
sys.path.append("..")
from config import MESH_ID_CONFIG
from scispacy.linking import EntityLinker
import json
import re
from transformers import pipeline

def clean_results(ner_results: list):
  ents = list()
  current_ent = ""
  add_to_current_ent = False
  for result in ner_results:
    # Determine if we need to add to the current word
    add_to_current_ent = True if result["entity"][0] != '0' else False

    # Add parts of the word slowly to the list
    if add_to_current_ent:
      current_ent += result["word"] if result["word"] == '-' else " " + result["word"]

    # Restart process depending on if there is no longer an entity
    if not add_to_current_ent and current_ent != "":
      ents.append(current_ent.replace("#", ""))
      current_ent = ""

  return ents

def clean_results_genetic(ner_results: list):
    ents = list()
    current_ent = ""
    for i, result in enumerate(ner_results):
      # Continuously add until the next word is seen
      if i != 0 and result["entity"][0] == 'B':
        ents.append(current_ent.replace("#", ""))
        current_ent = ""

      current_ent += " " + result["word"] if "#" not in result["word"] else result["word"]

    return ents + [current_ent.replace("#", "")]

class BioBERT_NER():
  def __init__(self):
    self.disease_pipe = pipeline("token-classification", model="alvaroalon2/biobert_diseases_ner")
    self.chemical_pipe = pipeline("token-classification", model="alvaroalon2/biobert_chemical_ner")
    self.genetic_pipe = pipeline("token-classification", model="alvaroalon2/biobert_genetic_ner")

  def get_clean_tokens(self, preprocessed_results: list):
    for i in range(len(preprocessed_results)):
      # For acronyms, remove extra spaces
      if preprocessed_results[i].isupper():
        preprocessed_results[i] = preprocessed_results[i].replace(" ", "")
        continue
      # For hyphens, remove the extra spaces after
      if '-' in preprocessed_results[i]:
        processed_word = ""
        for j in range(len(preprocessed_results[i])):
          # print(j, preprocessed_results[i][j], preprocessed_results[i][j - 1])
          if preprocessed_results[i][j - 1] == '-' and preprocessed_results[i][j].isspace():
            continue
          else:
            processed_word += preprocessed_results[i][j]
        preprocessed_results[i] = processed_word
      # In all cases, remove the first character which will be a space
      preprocessed_results[i] = preprocessed_results[i][1:]

    # There are some edge cases that are difficult, namely with spaces between words and hyphens
    # For hyphens, you can likely remove the space before if it's another word
    # For single words that re split up as tokens, if the tokens are all <=4 characters, 
    # it is likely that it is just one word that was split up
    for i, result in enumerate(preprocessed_results):
      # Check the hyphen case here
      if '-' in result and len(result) > 3:
        # Save the indexes where they are just spaces
        hyphen_indexes = [j - 1 for j in range(len(result)) if result[j] == '-']
        # Now add the characters to the new result so hyphenation is not a problem
        new_result = ""
        for j in range(len(result)):
           if j in hyphen_indexes:
              continue
           new_result += result[j]
        preprocessed_results[i] = new_result
      # Check the single word but multitoken case here
      possible_tokens = result.split()
      possibily_all_tokens = True
      for possible_token in possible_tokens:
        if len(possible_token) > 4:
          possibily_all_tokens = False
          break
      if possibily_all_tokens:
         preprocessed_results[i] = result.replace(" ", "")
          
    # To prevent a wasteful assignment, just return the preprocessed results
    # as postprocessed results
    return preprocessed_results

  def clean_results_disease(self, ner_results: list):
    ents = list()
    current_ent = ""
    add_to_current_ent = False
    for result in ner_results:
      # Determine if we need to add to the current word
      add_to_current_ent = True if result["entity"][0] != '0' else False

      # Add parts of the word slowly to the list
      if add_to_current_ent:
        current_ent += result["word"] if result["word"] == '-' else " " + result["word"]

      # Restart process depending on if there is no longer an entity
      if not add_to_current_ent and current_ent != "":
        ents.append(current_ent.replace("#", ""))
        current_ent = "" 

    return ents

  def clean_results_genetic(self, ner_results: list):
    ents = list()
    current_ent = ""
    for i, result in enumerate(ner_results):
      # Continuously add until the next word is seen
      if i != 0 and result["entity"][0] == 'B':
        ents.append(current_ent.replace("#", ""))
        current_ent = ""
      current_ent += " " + result["word"] if "#" not in result["word"] else result["word"]

    return ents + [current_ent.replace("#", "")]

  def complete_pipeline(self, pipeline, user_text: str):
    pipeline_results = pipeline(user_text)
    if pipeline == self.disease_pipe:
      ents = self.get_clean_tokens(self.clean_results_disease(pipeline_results))
      return [(ent, 'DISEASE') for ent in ents] 
    elif pipeline == self.chemical_pipe:
      ents = self.get_clean_tokens(self.clean_results_genetic(pipeline_results))
      return [(ent, 'CHEMICAL') for ent in ents]
    else:
      ents = self.get_clean_tokens(self.clean_results_genetic(pipeline_results))
      return [(ent, 'GENE_OR_GENE_PRODUCT') for ent in ents] 


  def get_entities(self, user_input: str):
    """
    The primary function that may be called across other classes and files.
    Returns all entities and their tags as a list.
    """
    all_entities = list()
    all_entities += self.complete_pipeline(self.disease_pipe, user_input)
    all_entities += self.complete_pipeline(self.chemical_pipe, user_input)
    all_entities += self.complete_pipeline(self.genetic_pipe, user_input)
    return all_entities

class SpacyNER:
    def __init__(self):
        self.disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
        self.scientific_entity_nlp = spacy.load("en_ner_bionlp13cg_md")
        self.pos_nlp = spacy.load("en_core_web_sm")
        self.graph_nodes = json.loads(open('data/node_records.json', "r").read())

        # ADDED RECENTLY
        # Might be able to get rid of some stuff above
        self.node_features = json.loads(open('/Users/josephramirez/2023-2024/llm-project/openai_sandbox/openai_api/data/node_features.json', 'r').read())

    def disease_ner(self, text: str):
        document = self.disease_ner_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]

    def scientific_entity_ner(self, text: str):
        document = self.scientific_entity_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]
    
    def get_entities(self, text: str):
        """
        The primary function to be used that will gather disease and scientific entites.
        Returns a list of tuples.

        Example usage:
        [(ent0, 'DISEASE'), (ent1, 'CHEMICAL')]
        """
        dis_ent = self.disease_ner(text)
        sci_ent = self.scientific_entity_ner(text)
        return dis_ent + sci_ent

    def part_of_speech_tags(self, text: str):
        """
        LEGACY
        """
        # pos_nlp = spacy.load("en_core_web_sm")
        document = self.pos_nlp(text)
        return [(token.text, token.pos_) for token in document]

    def show_entities(self, text: str):
        """
        LEGACY
        """
        # TODO: FIX DUE TO CHANGE IN get_entities()
        disease_ner_results, scientific_entity_ner_results, pos_results, mesh_ids = self.get_entities(text)

        print("DISEASES: {}".format(disease_ner_results))
        print("OTHER ENTITIES: {}".format(scientific_entity_ner_results))
        print("PARTS OF SPEECH: {}".format(pos_results))
        print("MESH IDS: {}".format(mesh_ids))

    def get_mesh_ids(self, text: str):
        """
        LEGACY
        """
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

class NamedEntityRecognition():
    def __init__(self):
       self.graph_nodes = json.loads(open('data/node_records.json', "r").read())
       self.node_features = json.loads(open('data/node_features.json', 'r').read())
       self.biobertner = BioBERT_NER()
       self.spacyner = SpacyNER()
    
    def clean_ner_results(self, initial_results: str) -> None:
        """
        Able to remove duplicate entity names between scientific and disease entities.
        Mainly to check duplicates between CHEMICAL (en_ner_bc5cdr_md) and 
        SIMPLE_CHEMICAL (en_ner_bionlp13cg_md).
        """
        to_remove = list()
        L = len(initial_results)

        # Double for loop but usually there are a few number of entities
        # Should not be a problem for time complexity
        for i in range(L):
           for j in range(i + 1, L):
              if initial_results[i][0] == initial_results[j][0] or initial_results[j][0] == '':
                 to_remove.append(j)
                 
        # Only add results not considered duplicate or empty
        cleaned_results = list()
        for i in range(L):
           if i in to_remove:
              continue
           cleaned_results.append(initial_results[i])
        
        return cleaned_results
    
    def full_ner(self, user_input: str):
       '''
       The primary function to be run in order to get a list of entities for a given text.
       '''
       # Get the results from each NER technique
       spacy_results = self.spacyner.get_entities(user_input)
       biobert_results = self.biobertner.get_entities(user_input)
       # Let full results be able to include other NER techniques if needed
       full_results = spacy_results + biobert_results
       cleaned_results = self.clean_ner_results(full_results)

       return cleaned_results
    
    def check_flipped(self, testing_entity: str, possible_name: str):
        """
        For the special case where there are two words in an entity but they may be flipped around.
        For now, this just deals with the case of 2 words.
        Ex. "synuclein alpha" should match to "alpha synuclein"
        """
        split_by_text = testing_entity.split()
        if len(split_by_text) >= 2:
            first_word = split_by_text[0]
            split_by_text.pop(0)
            split_by_text.append(first_word)
            testing_entity = ' '.join(split_by_text)
            if testing_entity in possible_name:
                return True
        return False
    
    def determine_match(self, testing_entity: str, possible_names: list):
       """
       For a given entity, determine if any names for a node match.
       """
       # NOTE: Removing dashes and replacing then with spaces for now 
       # There may be a better way of dealing with this later
       testing_entity = testing_entity.replace("-", " ")
       testing_entity = testing_entity.lower()
       for possible_name in possible_names:
            possible_name = possible_name.lower()
            if testing_entity in possible_name or self.check_flipped(testing_entity, possible_name):
                return True

       return False
    
    def format_context(self, context: list):
        """
        Format the context to easily send to the LLM.

        Example Usage
        The context my look like this: 
        [[('Mercuric Chloride', 'CHEMICAL'), ['MeSH_Compound:D008627', 'MeSH_Compound:C004925']], 
        [('neurotoxicity', 'DISEASE'), ['MeSH_Disease:D020261', 'MeSH_Disease:D020267', 'Reactome_Pathway:R-HSA-168799']], 
        [('Alpha-Synuclein', 'GENE_OR_GENE_PRODUCT'), ['Entrez:6622', 'Entrez:9627']]]

        We need the contex at the end to be simpler like this:

        """
        formatted_context = list()

        for ner_result in context:
            print(ner_result)
            # Check if there were no entities found
            if ner_result[1] == []:
                formatted_context.append((ner_result[0][0], []))
            else:
                for node_name in ner_result[1]:
                    formatted_context.append((ner_result[0][0], node_name))
        return formatted_context
    
    def generate_context(self, user_input: str):
        """
        O(NK), N: number of entities, K: number of node names. NO OPTIMIZATIONS.
        Usually N is small and N << K.

        Perform a search across all nodes listed in the KG.
        This may not be the best method, but given the size of the KG, it should be ok.
        For the future, you could try and extract what type of entity it would be based on NER results.

        WE WILL LATER USE THE ENTITIY TYPES FOR OPTIMIZATION.
        """
        # We will need to gather the NER results
        ner_results = self.full_ner(user_input)

        # Context variable will be a list of named entities and their node name type
        context = list()

        # For every NER result, check for the node somewhere in the graph
        for ner_result in ner_results:
            entity_context = [ner_result, []]
            for node in self.node_features:
                if "names" in self.node_features[node]:
                    node_names = self.node_features[node]["names"]
                    # For all of the node names, check if any of them are similar to the named entity
                    if type(node_names) == list:
                        if self.determine_match(ner_result[0], node_names):
                            entity_context[1] += [node]
                    else:
                       if self.determine_match(ner_result[0], [node_names]):
                            entity_context[1] += [node]
            context.append(entity_context)

        context = self.format_context(context)
        return context

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

    def get_node_in_graph(self, entity_name: str, possible_node_types: list) -> str:
        results = list()
        all_nodes = self.node_features.keys()
        # Check node type against similar node types
        for node_type in possible_node_types:
            # Need to get all possible types of names for the possible node types
            # Then, check if the entity name is anywhere in the list of names set up
            for node in all_nodes:
                # TODO: See if there is a better way of matching (semantic matching) that is also somewhat quick
                # my_dict.get(attribute_to_check) is not None
                if node_type in node and self.node_features[node].get('names') is not None:
                    lower_case_names = list(map(lambda x: x.lower(), self.node_features[node]['names']))
                    for lower_case_name in lower_case_names:
                        if entity_name.lower() in lower_case_name:
                            print(node)
                            results.append(node)
                            break
        return results
    
    def process_ner_results(self, ner_results: list):
        node_types = ['ATC', 'MeSH_Disease', 'biological_process', 'molecular_function', 'MeSH_Compound', 
                      'DrugBank_Compound', 'MeSH_Anatomy', 'KEGG_Pathway', 'MeSH_Tree_Disease', 'Reactome_Reaction', 
                      'MeSH_Tree_Anatomy', 'Reactome_Pathway', 'cellular_component', 'Entrez', 'UniProt']
        
        '''
        AMINO_ACID, ANATOMICAL_SYSTEM, CANCER, CELL, CELLULAR_COMPONENT, DEVELOPING_ANATOMICAL_STRUCTURE, 
        GENE_OR_GENE_PRODUCT, IMMATERIAL_ANATOMICAL_ENTITY, MULTI-TISSUE_STRUCTURE, ORGAN, 
        ORGANISM, ORGANISM_SUBDIVISION, ORGANISM_SUBSTANCE, PATHOLOGICAL_FORMATION, SIMPLE_CHEMICAL, TISSUE

        AMINO_ACID, ANATOMICAL_SYSTEM, CANCER, CELL, CELLULAR_COMPONENT, DEVELOPING_ANATOMICAL_STRUCTURE, 
        IMMATERIAL_ANATOMICAL_ENTITY, MULTI-TISSUE_STRUCTURE, ORGAN, 
        ORGANISM, ORGANISM_SUBDIVISION, ORGANISM_SUBSTANCE, PATHOLOGICAL_FORMATION, SIMPLE_CHEMICAL, TISSUE

        'ATC', '', 'biological_process', 'molecular_function', '', 
                      '', 'MeSH_Anatomy', 'KEGG_Pathway', 'MeSH_Tree_Disease', 'Reactome_Reaction', 
                      'MeSH_Tree_Anatomy', 'Reactome_Pathway', 'cellular_component', '', ''
        '''
        # NOTE: Build this incrementally
        # TODO: Finish matching the rest of the entities
        results = list()
        for ner_result in ner_results:
            entity_name = ner_result[0]
            entity_type = ner_result[1]

            
            if entity_type == 'DISEASE':
                results.append((entity_name, self.get_node_in_graph(entity_name, ['MeSH_Disease'])))
            elif entity_type == 'SIMPLE_CHEMICAL' or entity_type == 'CHEMICAL':
                results.append((entity_type, self.get_node_in_graph(entity_name, ['MeSH_Compound', 'DrugBank_Compound'])))
            else:
                results.append((entity_name, self.get_node_in_graph(entity_name, ['Entrez', 'UniProt'])))
        return results
    
    
if __name__ == "__main__":
   TEXT = "How viable is this hypothesis: Mercuric Chloride interacts with Alpha-Synuclein and other proteins involved in protein misfolding and aggregation pathways, exacerbating neurotoxicity."
#    TEXT = "What mesh compounds which are drugs act as chelators for Alpha-2-Z-globulin"
#    TEXT = "What mesh compounds block BFGFR and are in the PPI network of Cadherin"
#    TEXT = "What proteins share the same biological processes as dystrophin and KGFR?"
#    TEXT = "What antibodies exist for Leukocyte surface antigen?"
   full = NamedEntityRecognition()
   res = full.generate_context(TEXT)
#    res = full.full_ner(TEXT)
   print(res)
