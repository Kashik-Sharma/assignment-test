import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict
import uvicorn

from vectorization.embedding_ingestion import initialize_client

# Initialize FastAPI app
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Request model for FastAPI
class QueryRequest(BaseModel):
    query_text: str


def query_similar_chunks(query_text: str, top_k=3):
    """

    :param query_text:
    :param collection:
    :param top_k:
    :return:
    """
    try:
        collection = initialize_client()
        # Perform similarity search (find the top-k most similar embeddings in the collection)
        results = collection.query(
            query_texts=query_text,
            n_results=top_k
        )

        # Return the documents and their similarity scores
        return results['documents'], results['distances']

    except Exception as e:
        logger.error(f"Error querying ChromaDB: {e}")
        raise


# FastAPI route for querying based on the provided text prompt
@app.post("/query")
async def query(query_request: QueryRequest):
    try:
        # Get the query text from the request body
        query_text = query_request.query_text
        logger.info((f"query_text - {query_text}"))

        if not query_text:
            raise HTTPException(status_code=400, detail="No query text provided")

        # Initialize ChromaDB collection
        # collection = initialize_client()

        # Query similar chunks from ChromaDB
        similar_documents, distances = query_similar_chunks(query_text)

        # Return the results as a JSON response
        results = [{"document": doc, "distance": dist} for doc, dist in zip(similar_documents, distances)]
        return {"results": results}

    except Exception as e:
        logger.error(f"Error processing the query: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the query process")


# FastAPI route for home page
@app.get("/")
def home():
    return {"message": "Welcome to the ChromaDB Query API!"}


# Run the API with uvicorn if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
