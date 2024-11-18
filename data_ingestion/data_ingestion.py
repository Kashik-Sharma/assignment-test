import os
import logging
from pymongo import MongoClient, errors
import pandas as pd
from faker import Faker
import time

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Initialize Faker instance for generating fake data
fake = Faker()

# MongoDB connection setup
def connect_to_mongo():
    try:
        client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
        db = client['llm_data_engineer']  # Database name
        logger.info("Connected to MongoDB.")
        return db
    except errors.ConnectionError as e:
        logger.error(f"MongoDB connection error: {e}")
        raise

# Data ingestion function
def ingest_data_to_mongo(db, users_file, products_file, sales_file):
    try:
        # Load data from CSV files
        users_df = pd.read_csv(users_file)
        products_df = pd.read_csv(products_file)
        sales_df = pd.read_csv(sales_file)
        logger.info("Data loaded from CSV files.")

        # Convert DataFrames to dictionaries for MongoDB
        users_dict = users_df.to_dict(orient='records')
        products_dict = products_df.to_dict(orient='records')
        sales_dict = sales_df.to_dict(orient='records')

        # Insert data into MongoDB collections
        users_collection = db['users']
        products_collection = db['products']
        sales_collection = db['sales']

        users_collection.insert_many(users_dict)
        products_collection.insert_many(products_dict)
        sales_collection.insert_many(sales_dict)
        logger.info("Data successfully inserted into MongoDB collections.")

        # Create indexes for optimization
        sales_collection.create_index([("user_id", 1)])
        sales_collection.create_index([("product_id", 1)])
        sales_collection.create_index([("transaction_date", 1)])
        logger.info("Indexes created for sales collection.")
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        raise

# Fake data generation for reviews and descriptions
def generate_fake_reviews_and_descriptions(db, products_dict):
    try:
        reviews_collection = db['reviews']
        descriptions_collection = db['descriptions']

        # Create fake reviews and descriptions
        reviews_dict = [{
            "product_id": product["product_id"],
            "review_text": fake.text(max_nb_chars=200)
        } for product in products_dict]

        descriptions_dict = [{
            "product_id": product["product_id"],
            "product_description": fake.paragraph(nb_sentences=3)
        } for product in products_dict]

        # Insert reviews and descriptions into MongoDB
        reviews_collection.insert_many(reviews_dict)
        descriptions_collection.insert_many(descriptions_dict)

        # Create text indexes for unstructured data
        reviews_collection.create_index([("review_text", "text")])
        descriptions_collection.create_index([("product_description", "text")])
        logger.info("Fake reviews and descriptions generated and inserted with indexes.")
    except Exception as e:
        logger.error(f"Error generating fake reviews and descriptions: {e}")
        raise

# Main pipeline function
def run_pipeline():
    # Files to be loaded into MongoDB
    users_file = os.path.join(os.getcwd(), "data", "users.csv")
    products_file = os.path.join(os.getcwd(), "data", "products.csv")
    sales_file = os.path.join(os.getcwd(), "data", "sales.csv")
    
    db = connect_to_mongo()
    
    # Ingest data into MongoDB
    ingest_data_to_mongo(db, users_file, products_file, sales_file)
    
    # Generate and insert fake reviews and descriptions
    products_df = pd.read_csv(products_file)
    generate_fake_reviews_and_descriptions(db, products_df.to_dict(orient='records'))

    logger.info("Pipeline completed successfully.")

# Run the pipeline on a scheduled or triggered basis
if __name__ == "__main__":
    # while True:
    run_pipeline()
        # logger.info("Sleeping for 1 hour before running the pipeline again...")
        # time.sleep(3600)  # Sleep for 1 hour before running the pipeline again
        # print(os.getcwd())
