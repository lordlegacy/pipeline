import requests
from pymongo import MongoClient
from bson import ObjectId

# Connect to the MongoDB cluster
mongo_cluster = MongoClient("mongodb+srv://ondif:**************@red.felhxzd.mongodb.net/?retryWrites=true&w=majority")

# Access the 'shaft' database and 'shaftReadings' collection
db = mongo_cluster["shaft"]
collection_shaft_readings = db["shaftReadings"]

# Fetch the latest entry from MongoDB (you may need to customize the query)
latest_entry = collection_shaft_readings.find_one(sort=[('_id', -1)])

# Extract _id and timestamp from the fetched record
original_id = latest_entry.get('_id')
original_timestamp = ObjectId(original_id).generation_time

# Define the URL for making API requests
url = 'http://localhost:5000/predict_api'

# Prepare the new_sample_json using the fetched data
new_sample_json = {
    '_id': str(original_id),  # Convert ObjectId to string
    'timestamp': original_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Convert timestamp to ISO format string
    'Type': [latest_entry.get("Type", "N/A")],
    'Air temperature [K]': [latest_entry.get("Air temperature [K]", 0)],
    'Process temperature [K]': [latest_entry.get("Process temperature [K]", 0)],
    'Rotational speed [rpm]': [latest_entry.get("Rotational speed [rpm]", 0)],
    'Torque [Nm]': [latest_entry.get("Torque [Nm]", 0)],
    'Tool wear [min]': [latest_entry.get("Tool wear [min]", 0)],
}

# Make the API request
r = requests.post(url, json=new_sample_json)

# Parse the JSON response
prediction_result = r.json()

# Access the 'shaft' database and 'shaftStatus' collection
collection_shaft_status = db["shaftStatus"]

# Insert the prediction results into the MongoDB collection
post = {
    "_id": original_id,
    "timestamp": original_timestamp,
    "status": prediction_result.get("Predicted Target", "N/A"),
    "fType": prediction_result.get("Predicted Failure Type", "N/A")
}
collection_shaft_status.insert_one(post)

# Print the inserted document ID (optional)
print(f"Inserted document with ID: {post['_id']}")
print(r.json())
