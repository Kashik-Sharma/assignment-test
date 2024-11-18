import logging
from embedding_ingestion import add_single_chunk, add_batch_chunks, initialize_client

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def run_ingestion(text_chunks):
    """

    :param text_chunks:
    """
    try:
        collection = initialize_client()
        # Add a single chunk of text
        logger.info("Starting to add a single chunk of text.")
        single_chunk_id = add_single_chunk(collection, single_text, metadata)
        logger.info(f"Successfully added single chunk with ID: {single_chunk_id}")

        # Add a batch of chunks
        logger.info("Starting to add a batch of chunks.")
        batch_chunk_ids = add_batch_chunks(collection, batch_texts, [metadata] * len(batch_texts))
        logger.info(f"Successfully added batch chunks with IDs: {batch_chunk_ids}")

    except Exception as e:
        logger.error(f"An error occurred during ingestion: {e}")
        raise


if __name__ == "__main__":
    # Sample data for ingestion
    single_text = "This is a single chunk of text to add to ChromaDB."
    batch_texts = [
        "This is the first chunk in the batch.",
        "Here comes the second chunk in the batch.",
        "And this is the third chunk of text for the batch."
    ]

    # Sample metadata (optional)
    metadata = {"source": "user_review", "category": "feedback"}

    run_ingestion(None)
