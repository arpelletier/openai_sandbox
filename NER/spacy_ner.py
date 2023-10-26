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

    def show_entites(self, text: str):
        print("DISEASES: {}".format(self.disease_ner(text)))
        print("OTHER ENTITIES: {}".format(self.scientific_entity_ner(text)))
        print("PARTS OF SPEECH: {}".format(self.part_of_speech_tags(text)))
        print("MESH IDS: {}".format(self.get_mesh_ids(text)))

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


if __name__ == "__main__":
    prompt = "What drugs treat Crohn's disease?"

    ner = SpacyNER()
    ner.show_entites(prompt)
