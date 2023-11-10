# source: https://platform.openai.com/docs/guides/embeddings/embeddings

import sys
import openai
import pandas as pd

sys.path.append('..')
from config import OPENAI_KEY

openai.api_key = OPENAI_KEY


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


# df['ada_embedding'] = df.combined.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))
# df.to_csv('output/embedded_1k_reviews.csv', index=False)

def get_protein_embeddings(protein_to_description):
    prot_to_emb = {}
    for uniprot_id, description in protein_to_description.items():
        print(uniprot_id, description[:80], "...")  # print only first 80 characters of description
        emb = get_embedding(uniprot_id + " " + description)  # format as uniprot id + description
        print(str(emb)[:80] + "...")  # print only first 80 characters of embedding
        prot_to_emb[uniprot_id] = emb

    return prot_to_emb


def read_kg_proteins(input_file):
    kg_edges = pd.read_csv(input_file, sep="\t", header=None)
    kg_edges.columns = ['h', 'r', 't']
    nodes = set(kg_edges.h).union(set(kg_edges.t))
    proteins = [node for node in nodes if node.startswith('UniProt:')]
    genes = [node for node in nodes if node.startswith('Entrez:')]

    return proteins, genes


# Small handful of test embedding descriptions and accessions
protein_to_description = {
    'P05067': 'A4_HUMAN Amyloid-beta precursor protein. Function: Functions as a cell surface receptor and performs physiological functions on the surface of neurons relevant to neurite growth, neuronal adhesion and axonogenesis. Interaction between APP molecules on neighboring cells promotes synaptogenesis (PubMed:25122912). Involved in cell mobility and transcription regulation through protein-protein interactions. Can promote transcription activation through binding to APBB1-KAT5 and inhibits Notch signaling through interaction with Numb. Couples to apoptosis-inducing pathways such as those mediated by G(o) and JIP. Inhibits G(o) alpha ATPase activity (By similarity). Acts as a kinesin I membrane receptor, mediating the axonal transport of beta-secretase and presenilin 1 (By similarity). By acting as a kinesin I membrane receptor, plays a role in axonal anterograde transport of cargo towards synapes in axons (PubMed:17062754, PubMed:23011729). Involved in copper homeostasis/oxidative stress through copper ion reduction. In vitro, copper-metallated APP induces neuronal death directly or is potentiated through Cu2+-mediated low-density lipoprotein oxidation. Can regulate neurite outgrowth through binding to components of the extracellular matrix such as heparin and collagen I and IV. The splice isoforms that contain the BPTI domain possess protease inhibitor activity. Induces a AGER-dependent pathway that involves activation of p38 MAPK, resulting in internalization of amyloid-beta peptide and leading to mitochondrial dysfunction in cultured cortical neurons. Provides Cu2+ ions for GPC1 which are required for release of nitric oxide (NO) and subsequent degradation of the heparan sulfate chains on GPC1.',
    'Q9BYF1': 'ACE2_HUMAN Angiotensin-converting enzyme 2. Function: Essential counter-regulatory carboxypeptidase of the renin-angiotensin hormone system that is a critical regulator of blood volume, systemic vascular resistance, and thus cardiovascular homeostasis (PubMed:27217402). Converts angiotensin I to angiotensin 1-9, a nine-amino acid peptide with anti-hypertrophic effects in cardiomyocytes, and angiotensin II to angiotensin 1-7, which then acts as a beneficial vasodilator and anti-proliferation agent, counterbalancing the actions of the vasoconstrictor angiotensin II (PubMed:10969042, PubMed:10924499, PubMed:11815627, PubMed:19021774, PubMed:14504186). Also removes the C-terminal residue from three other vasoactive peptides, neurotensin, kinetensin, and des-Arg bradykinin, but is not active on bradykinin (PubMed:10969042, PubMed:11815627). Also cleaves other biological peptides, such as apelins (apelin-13, [Pyr1]apelin-13, apelin-17, apelin-36), casomorphins (beta-casomorphin-7, neocasomorphin) and dynorphin A with high efficiency (PubMed:11815627, PubMed:27217402, PubMed:28293165).',
    'P23458': 'JAK1_HUMAN Tyrosine-protein kinase JAK1. Function: Tyrosine kinase of the non-receptor type, involved in the IFN-alpha/beta/gamma signal pathway (PubMed:8232552, PubMed:7615558, PubMed:28111307, PubMed:32750333, PubMed:16239216). Kinase partner for the interleukin (IL)-2 receptor (PubMed:11909529) as well as interleukin (IL)-10 receptor (PubMed:12133952). Kinase partner for the type I interferon receptor IFNAR2 (PubMed:8232552, PubMed:7615558, PubMed:28111307, PubMed:32750333, PubMed:16239216). In response to interferon-binding to IFNAR1-IFNAR2 heterodimer, phosphorylates and activates its binding partner IFNAR2, creating docking sites for STAT proteins (PubMed:7759950). Directly phosphorylates STAT proteins but also activates STAT signaling through the transactivation of other JAK kinases associated with signaling receptors (PubMed:8232552, PubMed:16239216, PubMed:32750333).',
    'Q16644': 'MAPK3_HUMAN MAP kinase-activated protein kinase 3. Function: Stress-activated serine/threonine-protein kinase involved in cytokines production, endocytosis, cell migration, chromatin remodeling and transcriptional regulation. Following stress, it is phosphorylated and activated by MAP kinase p38-alpha/MAPK14, leading to phosphorylation of substrates. Phosphorylates serine in the peptide sequence, Hyd-X-R-X2-S, where Hyd is a large hydrophobic residue. MAPKAPK2 and MAPKAPK3, share the same function and substrate specificity, but MAPKAPK3 kinase activity and level in protein expression are lower compared to MAPKAPK2. Phosphorylates HSP27/HSPB1, KRT18, KRT20, RCSD1, RPS6KA3, TAB3 and TTP/ZFP36. Mediates phosphorylation of HSP27/HSPB1 in response to stress, leading to dissociate HSP27/HSPB1 from large small heat-shock protein (sHsps) oligomers and impair their chaperone activities and ability to protect against oxidative stress effectively. Involved in inflammatory response by regulating tumor necrosis factor (TNF) and IL6 production post-transcriptionally: acts by phosphorylating AU-rich elements (AREs)-binding proteins, such as TTP/ZFP36, leading to regulate the stability and translation of TNF and IL6 mRNAs. Phosphorylation of TTP/ZFP36, a major post-transcriptional regulator of TNF, promotes its binding to 14-3-3 proteins and reduces its ARE mRNA affinity leading to inhibition of dependent degradation of ARE-containing transcript. Involved in toll-like receptor signaling pathway (TLR) in dendritic cells: required for acute TLR-induced macropinocytosis by phosphorylating and activating RPS6KA3. Also acts as a modulator of Polycomb-mediated repression.',
    'P04637': 'P53_HUMAN Cellular tumor antigen p53 Function: Acts as a tumor suppressor in many tumor types; induces growth arrest or apoptosis depending on the physiological circumstances and cell type (PubMed:11025664, PubMed:12524540, PubMed:12810724, PubMed:15186775, PubMed:15340061, PubMed:17317671, PubMed:17349958, PubMed:19556538, PubMed:20673990, PubMed:20959462, PubMed:22726440, PubMed:24051492, PubMed:9840937, PubMed:24652652). Involved in cell cycle regulation as a trans-activator that acts to negatively regulate cell division by controlling a set of genes required for this process (PubMed:11025664, PubMed:12524540, PubMed:12810724, PubMed:15186775, PubMed:15340061, PubMed:17317671, PubMed:17349958, PubMed:19556538, PubMed:20673990, PubMed:20959462, PubMed:22726440, PubMed:24051492, PubMed:9840937, PubMed:24652652). One of the activated genes is an inhibitor of cyclin-dependent kinases. Apoptosis induction seems to be mediated either by stimulation of BAX and FAS antigen expression, or by repression of Bcl-2 expression. Its pro-apoptotic activity is activated via its interaction with PPP1R13B/ASPP1 or TP53BP2/ASPP2 (PubMed:12524540).'
}

k2bio_file = "../data/2023-08-18_know2bio_whole_kg.txt"
kg_proteins, kg_genes = read_kg_proteins(k2bio_file)

# TODO convert Entrez genes to NCBI genes, get descriptions, get embeddings

# Example of testing embedding on manual small dataset
prot_to_emb = get_protein_embeddings(protein_to_description)
