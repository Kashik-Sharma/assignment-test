from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
from vectorization.embedding_ingestion import initialize_client, add_batch_chunks
from query_n_retrieve.query_retrieve_api import query_similar_chunks
from llm.gemini_llm import generate
import logging
import io

# Initialize FastAPI app
app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Directory to store uploaded files
UPLOAD_DIR = "uploaded_files"

# Ensure the directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# Request model for FastAPI for querying
class QueryRequest(BaseModel):
    query_text: str


# Function to read and convert TXT file content into text
async def read_txt_file(txt_file: UploadFile):
    try:
        # Reset file pointer (if it's a spooled temporary file)
        txt_file.file.seek(0)  # Seek to the beginning of the file before reading

        # Read the file content asynchronously
        content = await txt_file.read()
        logger.info(f"File content length: {len(content)} bytes")

        # If content is empty, raise an error
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        # Decode byte content into a string
        text = content.decode('utf-8', errors='replace')

        # Log the first 1000 characters to verify
        logger.info(f"File content preview: {text[:1000]}...")

        return text
    except Exception as e:
        logger.error(f"Error processing TXT file: {e}")
        raise HTTPException(status_code=400, detail="Unable to process TXT file.")


# Function to split the text into chunks
def create_chunks_from_text(text, chunk_size=1000, chunk_overlap=100):
    try:
        # Split text into chunks
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        return chunks
    except Exception as e:
        logger.error(f"Error splitting text into chunks: {e}")
        raise HTTPException(status_code=500, detail="Error splitting text into chunks.")


# 1. Endpoint to upload and process a .txt file
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Check if file is a .txt file
        if not file.filename.lower().endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are allowed.")

        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File uploaded successfully: {file.filename}")

        # Read the .txt file content
        text = await read_txt_file(file)

        # Split the text into chunks
        chunk_list = create_chunks_from_text(text)

        if not chunk_list:
            raise HTTPException(status_code=500, detail="Error splitting text into chunks.")

        # Initialize ChromaDB client and store the chunks
        collection = initialize_client()
        chunk_ids = add_batch_chunks(collection, chunk_list)

        return {"message": "File processed and chunks added to ChromaDB.", "chunk_ids": chunk_ids}

    except Exception as e:
        logger.error(f"Error uploading and processing file: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")


# 2. Endpoint to query the ChromaDB and generate an answer
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
        context = "\n".join(similar_documents[0])

        # Use the Gemini model to generate an answer based on the context
        answer = generate(f"Given the following context, answer the question: {context} \nQuestion: {query_text}")

        # Return the answer as a JSON response
        return {"answer": answer}

    except Exception as e:
        logger.error(f"Error processing the query: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the query process.")


# 3. FastAPI route for home page
@app.get("/")
def home():
    return {"message": "Welcome to the RAG API!"}


# Run the API with uvicorn if this file is executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
