import chromadb
import logging
import os
import uuid

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# Initialize ChromaDB client inside a function
def initialize_client():
    try:
        # Set a local directory for ChromaDB storage
        LOCAL_STORAGE_PATH = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "..")),
                                          'chromadb_data')  # Define where to store ChromaDB data on the local disk
        logger.info(f"LOCAL_STORAGE_PATH- {LOCAL_STORAGE_PATH}")

        # Ensure the directory exists
        if not os.path.exists(LOCAL_STORAGE_PATH):
            os.makedirs(LOCAL_STORAGE_PATH)
            logger.info(f"Created directory for ChromaDB storage: {LOCAL_STORAGE_PATH}")
        else:
            logger.info(f"ChromaDB storage directory already exists: {LOCAL_STORAGE_PATH}")

        client = chromadb.PersistentClient(path=LOCAL_STORAGE_PATH)
        # Define the ChromaDB collection
        collection_name = "text_vectors"

        # Create or get the collection for storing text embeddings
        if collection_name not in str(client.list_collections()):
            collection = client.create_collection(name=collection_name)
            logger.info(f"Collection '{collection_name}' created.")
        else:
            collection = client.get_collection(collection_name)
            logger.info(f"Connected to ChromaDB collection: {collection_name}")

        return collection

    except Exception as e:
        logger.error(f"Error initializing ChromaDB client or collection: {e}")
        raise


# Method to add a single chunk (text) to ChromaDB
def add_single_chunk(collection, text, metadata=None):
    try:
        # Generate a unique ID for the chunk
        chunk_id = str(uuid.uuid4())

        # Generate embeddings for the chunk (Currently commented out, you should add real embeddings here)
        # embeddings = embedding_functions.HuggingFaceEmbeddingFunction(model_name="sentence-transformers/all-MiniLM-L6-v2",
        #                                                            api_key=HUGGINGFACE_API_KEY).embed([text])

        # Add the chunk (embedding) to ChromaDB
        collection.add(
            ids=[chunk_id],
            # embeddings=embeddings,
            metadatas=[metadata] if metadata else [{}],
            documents=[text]
        )
        logger.info(f"Added single chunk with ID: {chunk_id}")
        return chunk_id
    except Exception as e:
        logger.error(f"Error adding single chunk to ChromaDB: {e}")
        raise


def add_batch_chunks(collection, texts, metadata_list=None):
    try:
        # Generate unique IDs for the batch of chunks
        chunk_ids = [str(uuid.uuid4()) for _ in texts]

        # Ensure metadata list has the same length as texts
        if metadata_list is None:
            metadata_list = [{"test_key": "test_value"}] * len(texts)
        elif len(metadata_list) < len(texts):
            metadata_list.extend([{}] * (len(texts) - len(metadata_list)))

        # Add the batch of chunks (embeddings) to ChromaDB
        collection.add(
            ids=chunk_ids,
            metadatas=metadata_list,  # Ensure we pass metadata with every chunk
            documents=texts
        )
        logger.info(f"Added batch of {len(texts)} chunks to ChromaDB")
        return chunk_ids
    except Exception as e:
        logger.error(f"Error adding batch of chunks to ChromaDB: {e}")
        raise e


# if __name__ == "__main__":
#     print(os.path.join(os.getcwd(), 'chromadb_data'))
#     print(f'x -= { os.path.abspath(os.path.join(os.getcwd(), ".."))}')
