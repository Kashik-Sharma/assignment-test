from pymongo import MongoClient
import pandas as pd
import re
from nltk.corpus import stopwords

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['llm_data_engineer']

# Collections for raw data
raw_users_collection = db['users']
raw_products_collection = db['products']
raw_sales_collection = db['sales']

# Fetch raw data from MongoDB collections
raw_users = pd.DataFrame(list(raw_users_collection.find()))
raw_products = pd.DataFrame(list(raw_products_collection.find()))
raw_sales = pd.DataFrame(list(raw_sales_collection.find()))

# Clean column names to ensure no spaces or extra characters
raw_users.columns = raw_users.columns.str.strip()
raw_products.columns = raw_products.columns.str.strip()
raw_sales.columns = raw_sales.columns.str.strip()

# Check the first few rows of the data to confirm the column names
print(raw_users.columns)
print(raw_users.head())

# Preprocessing function for structured data with optimized storage
def preprocess_structured_data(data, collection_name):
    # Handle missing values based on the collection (columns vary)
    
    if collection_name == 'users':
        if 'age' in data.columns:
            data['age'] = data['age'].fillna(data['age'].median())  # Fill missing age with median
        if 'country' in data.columns:
            data['country'] = data['country'].fillna('Unknown')  # Fill missing country with 'Unknown'
    
    elif collection_name == 'products':
        if 'category' in data.columns:
            data['category'] = data['category'].fillna('Miscellaneous')  # Handle missing category
        if 'price' in data.columns:
            data['price'] = pd.to_numeric(data['price'], errors='coerce')  # Ensure price is numeric
    
    elif collection_name == 'sales':
        if 'transaction_date' in data.columns:
            data['transaction_date'] = pd.to_datetime(data['transaction_date'], errors='coerce').dt.strftime('%Y-%m-%d')  # Standardize date format
    
    # Remove duplicates for all collections
    data = data.drop_duplicates()
    
    # Return cleaned data
    return data

# Preprocessing function for unstructured data (e.g., reviews and descriptions)
def preprocess_text_data(text_data):
    # Remove special characters, digits, and extra spaces
    text_data = text_data.apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', str(x)))
    
    # Convert to lowercase
    text_data = text_data.apply(lambda x: x.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    text_data = text_data.apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
    
    # Remove extra spaces
    text_data = text_data.apply(lambda x: ' '.join(x.split()))
    
    return text_data

# Apply preprocessing to each dataset with the correct collection name
cleaned_users = preprocess_structured_data(raw_users, 'users')
cleaned_products = preprocess_structured_data(raw_products, 'products')
cleaned_sales = preprocess_structured_data(raw_sales, 'sales')

# Preprocess unstructured data (reviews and descriptions)
cleaned_reviews = pd.DataFrame(list(db['reviews'].find()))
cleaned_reviews['review_text'] = preprocess_text_data(cleaned_reviews['review_text'])

cleaned_descriptions = pd.DataFrame(list(db['descriptions'].find()))
cleaned_descriptions['product_description'] = preprocess_text_data(cleaned_descriptions['product_description'])

# Insert cleaned reviews and descriptions
db['cleaned_reviews'].insert_many(cleaned_reviews.to_dict(orient='records'))
db['cleaned_descriptions'].insert_many(cleaned_descriptions.to_dict(orient='records'))

# Save cleaned data back to MongoDB (new collections)
cleaned_users_collection = db['cleaned_users']
cleaned_products_collection = db['cleaned_products']
cleaned_sales_collection = db['cleaned_sales']

cleaned_users_collection.insert_many(cleaned_users.to_dict(orient='records'))
cleaned_products_collection.insert_many(cleaned_products.to_dict(orient='records'))
cleaned_sales_collection.insert_many(cleaned_sales.to_dict(orient='records'))

print("Preprocessing completed and data saved in new collections.")
