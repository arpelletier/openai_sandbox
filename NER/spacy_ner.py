import spacy
# from config import MESH_ID_CONFIG
from scispacy.linking import EntityLinker

class SpacyNER:
    def __init__(self):
        self.disease_ner_nlp = spacy.load("en_ner_bc5cdr_md")
        self.scientific_entity_nlp = spacy.load("en_ner_bionlp13cg_md")
        # self.pos_nlp = spacy.load("en_core_web_sm")

    def disease_ner(self, text: str):
        document = self.disease_ner_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]

    def scientific_entity_ner(self, text: str):
        document = self.scientific_entity_nlp(text)
        return [(ent.text, ent.label_) for ent in document.ents]
    
    def get_ner_results(self, text: str):
        dis_ent = self.disease_ner(text)
        sci_ent = self.scientific_entity_ner(text)
        return dis_ent + sci_ent

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
    TEXT = """In addition to their essential catalytic role in protein biosynthesis, aminoacyl-tRNA synthetases participate in numerous other functions, 
    including regulation of gene expression and amino acid biosynthesis via transamidation pathways. Herein, we describe a class of aminoacyl-tRNA synthetase-like 
    (HisZ) proteins based on the catalytic core of the contemporary class II histidyl-tRNA synthetase whose members lack aminoacylation activity but are instead essential 
    components of the first enzyme in histidine biosynthesis ATP phosphoribosyltransferase (HisG). Prediction of the function of HisZ in Lactococcus lactis was 
    assisted by comparative genomics, a technique that revealed a link between the presence or the absence of HisZ and a systematic variation in the length of the HisG polypeptide. 
    HisZ is required for histidine prototrophy, and three other lines of evidence support the direct involvement of HisZ in the transferase function. 
    (i) Genetic experiments demonstrate that complementation of an in-frame deletion of HisG from Escherichia coli (which does not possess HisZ) requires both HisG and HisZ from L. lactis. 
    (ii) Coelution of HisG and HisZ during affinity chromatography provides evidence of direct physical interaction. 
    (iii) Both HisG and HisZ are required for catalysis of the ATP phosphoribosyltransferase reaction. 
    This observation of a common protein domain linking amino acid biosynthesis and protein synthesis implies an early connection between the biosynthesis of amino acids and proteins."""

    TEXT = 'The presence of conserved phosphorylation sites in the regulatory domain of Protein Z suggests that phosphorylation may play a role in modulating its activity.'

    TEXT = 'How viable is this hypothesis: Mercuric Chloride interacts with Alpha-Synuclein and other proteins involved in protein misfolding and aggregation pathways, exacerbating neurotoxicity.'

    ner = SpacyNER()
    ner_res = ner.get_ner_results(TEXT)
    print(ner_res)