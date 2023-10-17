import scispacy
import spacy
from scispacy.umls_linking import UmlsEntityLinker
from collections import OrderedDict

def disease_ner(text: str):
    disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
    document = disease_ner_nlp(text)
    return [(ent.text, ent.label_) for ent in document.ents]

def scientific_entity_ner(text: str):
    disease_ner_nlp = spacy.load("en_ner_bionlp13cg_md")
    document = disease_ner_nlp(text)
    return [(ent.text, ent.label_) for ent in document.ents]

def part_of_speech_tags(text: str):
    pos_nlp = spacy.load("en_core_web_sm")
    document = pos_nlp(text)
    return [(token.text, token.pos_) for token in document]

def unified_medical_lang_entity(spacy_model, document):
    nlp = spacy.load(spacy_model)
    linker = UmlsEntityLinker(k=10)
    # nlp.add_pipe(linker)
    nlp.add_pipe('scispacy_linker')
    doc = nlp(document)
    entity = doc.ents
    entity = [str(item) for item in entity]
    entity = str(OrderedDict.fromkeys(entity))
    entity = nlp(entity).ents
    for entity in entity:
        import pdb;pdb.set_trace()
        for umls_ent in entity._.umls_ents:
            print("Entity name: ", entity)
            Concept_id, score = umls_ent
            print("concept-id", Concept_id)
            print("score", score)
            print(linker.umls.cui_to_entity[umls_ent[0]])


def show_entites(text: str):
    print("DISEASES: {}".format(disease_ner(text)))
    print("OTHER ENTITIES: {}".format(scientific_entity_ner(text)))
    print("PARTS OF SPEECH: {}".format(part_of_speech_tags(text)))

"""
Save link for possible future function that uses UMLS
https://oyewusiwuraola.medium.com/how-to-use-scispacy-for-biomedical-named-entity-recognition-abbreviation-resolution-and-link-umls-87d3f7c08db2
"""

# with open("prompts.txt", "r") as f:
#     for prompt in f:
#         print("PROMPT: {}".format(prompt))
#         show_entites(prompt)
#         print()

if __name__ == "__main__":
    # show_entites("What are drugs used for treating breast cancer")
    # import pdb;pdb.set_trace()
    unified_medical_lang_entity("en_ner_bc5cdr_md", "What are drugs used for treating breast cancer")