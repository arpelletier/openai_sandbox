import spacy, scispacy
from scispacy.linking import EntityLinker

MESH_ID_CONFIG = {
"resolve_abbreviations": True,  
"linker_name": "mesh", 
"max_entities_per_mention":1
}

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

def show_entites(text: str):
    print("DISEASES: {}".format(disease_ner(text)))
    print("OTHER ENTITIES: {}".format(scientific_entity_ner(text)))
    print("PARTS OF SPEECH: {}".format(part_of_speech_tags(text)))

def get_mesh_ids(text: str, model='en_ner_bc5cdr_md'):
    """Return mesh ids for named entites."""
    # Load in proper NLP 
    nlp = spacy.load(model)
    nlp.add_pipe("scispacy_linker", config=MESH_ID_CONFIG)
    linker = nlp.get_pipe("scispacy_linker")
    # Find the knowledge base entities
    doc = nlp(text)
    for e in doc.ents:
        if e._.kb_ents:
            cui = e._.kb_ents[0][0]
            print(e, cui)

if __name__ == "__main__":
    get_mesh_ids("What drugs treat Crohn's disease?")
