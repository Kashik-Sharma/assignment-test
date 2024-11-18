from data_preprocessing.text_preprocessing_for_chroma import *
from vectorization.embedding_ingestion import *
from query_n_retrieve.query_retrieve_api import *

from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from data_preprocessing.text_preprocessing_for_chroma import FileProcessor, ChunkHandler
from vectorization.embedding_ingestion import initialize_client, add_batch_chunks
import logging

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


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File uploaded successfully: {file.filename}")

        # Process the file (convert to text)
        text = FileProcessor.process_file(file)

        if not text:
            raise HTTPException(status_code=400, detail="Unsupported file format or unable to process file.")

        # Create chunks from the text
        chunk_list = ChunkHandler.langchain_create_chunk_from_text(text)

        if not chunk_list:
            raise HTTPException(status_code=500, detail="Error splitting text into chunks.")

        # Initialize ChromaDB client and store the chunks
        collection = initialize_client()
        chunk_ids = add_batch_chunks(collection, [chunk.page_content for chunk in chunk_list])

        return {"message": "File processed and chunks added to ChromaDB.", "chunk_ids": chunk_ids}

    except Exception as e:
        logger.error(f"Error uploading and processing file: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

