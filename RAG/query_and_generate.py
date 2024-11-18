from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query_n_retrieve.query_retrieve_api import query_similar_chunks
from llm.gemini_llm import generate
import logging

# Initialize FastAPI app
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Request model for FastAPI
class QueryRequest(BaseModel):
    query_text: str

@app.post("/query")
async def query(query_request: QueryRequest):
    try:
        # Get the query text from the request body
        query_text = query_request.query_text
        logger.info(f"Query received: {query_text}")

        if not query_text:
            raise HTTPException(status_code=400, detail="No query text provided")

        # Retrieve similar chunks from ChromaDB
        similar_documents, distances = query_similar_chunks(query_text)

        # Combine similar chunks into a single context
        context = "\n".join(similar_documents)

        # Use the Gemini model to generate an answer based on the context
        answer = generate(f"Given the following context, answer the question: {context} \nQuestion: {query_text}")

        # Return the answer as a JSON response
        return {"answer": answer}

    except Exception as e:
        logger.error(f"Error processing the query: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the query process.")
