import json
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings


class VectorStore():
    def __init__(self):
        self.node_features_file = 'data/node_features.json'
        self.node_features = json.load(open('data/node_features.json','r'))
    
    def prepare_node_data(self, node_feature_file):
        ''' This function extracts the names and description for nodes from the node feature json file. '''
        # Read file
        node_features = json.load(open(self.node_features_file,'r'))
        
        # Combine and extract node name followed by description
        node_to_descriptor = {}
        for node, n_features in node_features.items():
            desc = f"node_name: {node}. "
            if 'names' in n_features:
                names = n_features['names'] # some are strings
                if isinstance(names, list): # some are lists, need to format
                    names = ", ".join(names)
                desc += f"Names: {names}. "
            if 'description' in n_features:
                desc += f"Description: {n_features['description']}. "
            node_to_descriptor[node] = desc[:-1] # assign and remove trailing space
        return node_to_descriptor
    
    def prepare_node_descriptions_for_rag(self, node_to_descriptor):
        list_of_documents = []
        for k, v in node_to_descriptor.items():
            doc = Document(page_content=v,metadata=dict(node_name=k))
            list_of_documents += [doc]
        return list_of_documents 
    
    def save_vector_store(self, debug=True):
        node_to_descriptor = self.prepare_node_data(self.node_features_file)
        node_rag_corpus = self.prepare_node_descriptions_for_rag(node_to_descriptor)

        if debug:
            print('Splitting documents into chunks')

        # Split documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=20, chunk_overlap=10) 
        # Might need to play around with these settings
        data = text_splitter.split_documents(node_rag_corpus)

        if debug:
            print('Creating vector store')

        # Create vector store
        emb_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(data, embedding=emb_model)

        if debug:
            print('Saving vector store')

        # Save vector store
        vectorstore.save_local("k2bio_node_descriptors_faiss_index")

        if debug:
            print('PROCESS COMPLETED')

if __name__ == '__main__':
    vector_store = VectorStore()
    vector_store.save_vector_store()

