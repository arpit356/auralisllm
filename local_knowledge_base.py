import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader

# --- Configuration ---
DATASET_DIR = "dataset"
DB_DIR = "chroma_db"
COLLECTION_NAME = "auralis_knowledge"

def build_knowledge_base():
    """Reads all .txt, .pdf, and .docx files from the dataset folder and saves embeddings locally."""
    print(f"Building local knowledge base from {DATASET_DIR} folder...")
    
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"Created {DATASET_DIR} folder. Please add documents and run again.")
        return

    # 1. Setup Local ChromaDB
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Recreate collection to ensure a fresh index
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)
    
    chunked_docs = []
    chunked_metadatas = []
    ids = []
    file_count = 0

    for filename in os.listdir(DATASET_DIR):
        file_path = os.path.join(DATASET_DIR, filename)
        loader = None
        
        if filename.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            
        if loader:
            try:
                raw_docs = loader.load()
                # Split the documents from this specific file
                chunks = text_splitter.split_documents(raw_docs)
                
                for i, chunk in enumerate(chunks):
                    chunked_docs.append(chunk.page_content)
                    chunked_metadatas.append({"source": filename})
                    ids.append(f"{filename}_{i}")
                
                file_count += 1
                print(f"Successfully processed: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    if not chunked_docs:
        print("No valid documents found in dataset folder.")
        return

    print(f"Split {file_count} files into {len(chunked_docs)} chunks.")
    print("Embedding and saving to local database. This might take a moment...")
    
    # Add data in batches
    batch_size = 5000
    for i in range(0, len(chunked_docs), batch_size):
        end_idx = min(i + batch_size, len(chunked_docs))
        collection.add(
            documents=chunked_docs[i:end_idx],
            metadatas=chunked_metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
    
    print("[OK] Local knowledge base built successfully!")

# --- Global Cache for Performance ---
CHROMA_CLIENT = None
EMBEDDING_FUNCTION = None
COLLECTION = None

def get_collection():
    """Helper to get a cached collection instance."""
    global CHROMA_CLIENT, EMBEDDING_FUNCTION, COLLECTION
    if COLLECTION is None:
        if not os.path.exists(DB_DIR):
            return None
        CHROMA_CLIENT = chromadb.PersistentClient(path=DB_DIR)
        EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        COLLECTION = CHROMA_CLIENT.get_collection(name=COLLECTION_NAME, embedding_function=EMBEDDING_FUNCTION)
    return COLLECTION

def search_knowledge_base(query, n_results=3):
    """Searches the local database for relevant text with caching."""
    collection = get_collection()
    if not collection:
        return ""
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results and results['documents'] and results['documents'][0]:
            return "\n---\n".join(results['documents'][0])
            
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        
    return ""

if __name__ == "__main__":
    build_knowledge_base()
