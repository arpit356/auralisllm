import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuration ---
DATASET_DIR = "dataset"
DB_DIR = "chroma_db"
COLLECTION_NAME = "auralis_knowledge"

def load_text_files(directory):
    """Simple function to read all text files from the dataset directory."""
    documents = []
    metadata = []
    
    if not os.path.exists(directory):
        print(f"Warning: Dataset directory '{directory}' not found.")
        return documents, metadata

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(content)
                    metadata.append({"source": filename})
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                
    return documents, metadata

def build_knowledge_base():
    """Reads dataset, chunks it, and saves embeddings locally."""
    print("Building local knowledge base from dataset folder...")
    
    documents, metadatas = load_text_files(DATASET_DIR)
    
    if not documents:
        print("No .txt files found in dataset folder to build knowledge base.")
        return None
        
    # 1. Chunking: Large documents need to be split into smaller pieces
    # so the AI can retrieve just the most relevant sections.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Characters per chunk
        chunk_overlap=50 # Overlap to maintain context between chunks
    )
    
    chunked_docs = []
    chunked_metadatas = []
    ids = []
    
    for i, doc in enumerate(documents):
        chunks = text_splitter.split_text(doc)
        for j, chunk in enumerate(chunks):
            chunked_docs.append(chunk)
            chunked_metadatas.append(metadatas[i])
            ids.append(f"doc_{i}_chunk_{j}")
            
    print(f"Split {len(documents)} documents into {len(chunked_docs)} chunks.")

    # 2. Setup Local ChromaDB
    # This stores the embeddings directly on the hard drive (no server needed)
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    
    # Use a small, efficient embedding model that downloads automatically
    # sentence-transformers/all-MiniLM-L6-v2 is standard and very fast on CPU
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # 3. Create or Get Collection
    # chroma will automatically embed the text when we add it
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=sentence_transformer_ef
    )
    
    # Clear existing data so we don't have duplicates if we run this multiple times
    try:
        if collection.count() > 0:
            print("Clearing old knowledge base data...")
            # We recreate the collection for simplicity
            chroma_client.delete_collection(COLLECTION_NAME)
            collection = chroma_client.create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
    except Exception:
        pass # Handle case where count might fail on empty new collection

    print("Embedding and saving to local database. This might take a moment...")
    
    # Add data to the database in batches to avoid max batch size limits
    batch_size = 5000
    for i in range(0, len(chunked_docs), batch_size):
        end_idx = min(i + batch_size, len(chunked_docs))
        print(f"Adding batch {i} to {end_idx}...")
        collection.add(
            documents=chunked_docs[i:end_idx],
            metadatas=chunked_metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )

    
    print("✅ Local knowledge base built successfully!")
    return collection

def search_knowledge_base(query, n_results=5):
    """Searches the local database for relevant text."""
    if not os.path.exists(DB_DIR):
        return ""
        
    try:
        chroma_client = chromadb.PersistentClient(path=DB_DIR)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Combine the top matching text chunks into a single string
        if results and results['documents'] and results['documents'][0]:
            context = "\n---\n".join(results['documents'][0])
            return context
            
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        
    return ""

if __name__ == "__main__":
    build_knowledge_base()
    
    # Test search
    # test_context = search_knowledge_base("What is our policy?")
    # print(f"\nTest Search Result:\n{test_context}")
