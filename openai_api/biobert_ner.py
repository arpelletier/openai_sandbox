from transformers import pipeline

class BioBERT_NER():
  def __init__(self):
    self.disease_pipe = pipeline("token-classification", model="alvaroalon2/biobert_diseases_ner")
    self.chemical_pipe = pipeline("token-classification", model="alvaroalon2/biobert_chemical_ner")
    self.genetic_pipe = pipeline("token-classification", model="alvaroalon2/biobert_genetic_ner")
  
  def clean_pipeline_results(self, pipeline_results: list):
    '''
    From the NER pipelines, clean the tokenized results.

    Returns a list of entities based on the BIO method. Results may lack spaces between words.
    '''
    results = list()

    current_word = ''
    for result in pipeline_results:
      if result['entity'] == '0':
        continue
      else:
        if current_word != '' and result['entity'][0] == 'B':
          results.append(current_word)
          current_word = ''
        current_word += result['word'].replace('#', '')

    results.append(current_word) 
    
    # Prevent accidentally returning '' as the first string
    if results[0] == '':
      results = results[1:]

    return results
    
  def get_entities(self, text):
    disease = self.clean_pipeline_results(self.disease_pipe(text))
    gene = self.clean_pipeline_results(self.genetic_pipe(text))
    chemical = self.clean_pipeline_results(self.chemical_pipe(text))
    return disease + chemical + gene

#   def get_clean_tokens(self, preprocessed_results: list):
#     for i in range(len(preprocessed_results)):
#       # For acronyms, remove extra spaces
#       if preprocessed_results[i].isupper():
#         preprocessed_results[i] = preprocessed_results[i].replace(" ", "")
#         continue
#       # For hyphens, remove the extra spaces after
#       if '-' in preprocessed_results[i]:
#         processed_word = ""
#         for j in range(len(preprocessed_results[i])):
#           # print(j, preprocessed_results[i][j], preprocessed_results[i][j - 1])
#           if preprocessed_results[i][j - 1] == '-' and preprocessed_results[i][j].isspace():
#             continue
#           else:
#             processed_word += preprocessed_results[i][j]
#         preprocessed_results[i] = processed_word
#       # In all cases, remove the first character which will be a space
#       preprocessed_results[i] = preprocessed_results[i][1:]

#     # There are some edge cases that are difficult, namely with spaces between words and hyphens
#     # For hyphens, you can likely remove the space before if it's another word
#     # For single words that re split up as tokens, if the tokens are all <=4 characters, 
#     # it is likely that it is just one word that was split up
#     for i, result in enumerate(preprocessed_results):
#       # Check the hyphen case here
#       if '-' in result and len(result) > 3:
#         # Save the indexes where they are just spaces
#         hyphen_indexes = [j - 1 for j in range(len(result)) if result[j] == '-']
#         # Now add the characters to the new result so hyphenation is not a problem
#         new_result = ""
#         for j in range(len(result)):
#            if j in hyphen_indexes:
#               continue
#            new_result += result[j]
#         preprocessed_results[i] = new_result
#       # Check the single word but multitoken case here
#       possible_tokens = result.split()
#       possibily_all_tokens = True
#       for possible_token in possible_tokens:
#         if len(possible_token) > 4:
#           possibily_all_tokens = False
#           break
#       if possibily_all_tokens:
#          preprocessed_results[i] = result.replace(" ", "")
          
#     # To prevent a wasteful assignment, just return the preprocessed results
#     # as postprocessed results
#     return preprocessed_results

#   def clean_results_disease(self, ner_results: list):
#     ents = list()
#     current_ent = ""
#     add_to_current_ent = False
#     for result in ner_results:
#       # Determine if we need to add to the current word
#       add_to_current_ent = True if result["entity"][0] != '0' else False

#       # Add parts of the word slowly to the list
#       if add_to_current_ent:
#         current_ent += result["word"] if result["word"] == '-' else " " + result["word"]

#       # Restart process depending on if there is no longer an entity
#       if not add_to_current_ent and current_ent != "":
#         ents.append(current_ent.replace("#", ""))
#         current_ent = "" 

#     return ents

#   def clean_results_genetic(self, ner_results: list):
#     ents = list()
#     current_ent = ""
#     for i, result in enumerate(ner_results):
#       # Continuously add until the next word is seen
#       if i != 0 and result["entity"][0] == 'B':
#         ents.append(current_ent.replace("#", ""))
#         current_ent = ""
#       current_ent += " " + result["word"] if "#" not in result["word"] else result["word"]

#     return ents + [current_ent.replace("#", "")]

#   def complete_pipeline(self, pipeline, user_text: str):
#     pipeline_results = pipeline(user_text)
#     if pipeline == self.disease_pipe:
#       ents = self.get_clean_tokens(self.clean_results_disease(pipeline_results))
#       return [(ent, 'DISEASE') for ent in ents] 
#     elif pipeline == self.chemical_pipe:
#       ents = self.get_clean_tokens(self.clean_results_genetic(pipeline_results))
#       return [(ent, 'CHEMICAL') for ent in ents]
#     else:
#       ents = self.get_clean_tokens(self.clean_results_genetic(pipeline_results))
#       return [(ent, 'GENE_OR_GENE_PRODUCT') for ent in ents] 


#   def get_entities(self, user_input: str):
#     """
#     The primary function that may be called across other classes and files.
#     Returns all entities and their tags as a list.
#     """
#     all_entities = list()
#     all_entities += self.complete_pipeline(self.disease_pipe, user_input)
#     all_entities += self.complete_pipeline(self.chemical_pipe, user_input)
#     all_entities += self.complete_pipeline(self.genetic_pipe, user_input)
#     return all_entities
  
if __name__ == "__main__":
  foo = BioBERT_NER()
  text = "How viable is this hypothesis: Mercuric Chloride interacts with Alpha-Synuclein and other proteins involved in protein misfolding and aggregation pathways, exacerbating neurotoxicity"
  bar = foo.foo(text)    
  print(bar)