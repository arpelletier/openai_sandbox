import spacy
from config import MESH_ID_CONFIG
from scispacy.linking import EntityLinker

class SpacyNER:
    def __init__(self):
        self.disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
        self.scientific_entity_nlp = spacy.load("en_ner_bionlp13cg_md")
        self.pos_nlp = spacy.load("en_core_web_sm")

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
        disease_ner_results, scientific_entity_ner_results, pos_results, mesh_ids = self.get_entites(text)

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
        disease_ner_results = self.disease_ner(text)
        scientific_entity_ner_results = self.scientific_entity_ner(text)
        pos_results = self.part_of_speech_tags(text)
        mesh_ids = self.get_mesh_ids(text)

        return disease_ner_results, scientific_entity_ner_results, pos_results, mesh_ids


if __name__ == "__main__":
    prompt = "What drugs treat Crohn's disease?"

    ner = SpacyNER()
    ner.show_entities(prompt)
