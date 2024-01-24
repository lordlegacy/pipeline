import requests
from pymongo import MongoClient
from bson import ObjectId
from threading import Thread

# Connect to the MongoDB cluster
mongo_cluster = MongoClient("mongodb+srv://ondif:churchilchurchil@red.felhxzd.mongodb.net/?retryWrites=true&w=majority")

# Access the 'shaft' database and 'shaftReadings' collection
db = mongo_cluster["shaft"]
collection_shaft_readings = db["shaftReadings"]

# Access the 'shaft' database and 'shaftStatus' collection
collection_shaft_status = db["shaftStatus"]

# Define the URL for making API requests
url = 'http://localhost:5000/predict_api'

def process_new_entry(new_entry):
    try:
        # Extract _id and timestamp from the fetched record
        original_id = new_entry.get('_id')
        original_timestamp = ObjectId(original_id).generation_time

        # Prepare the new_sample_json using the fetched data
        new_sample_json = {
            '_id': str(original_id),  # Convert ObjectId to string
            'timestamp': original_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Convert timestamp to ISO format string
            'Type': [new_entry.get("Type", "N/A")],
            'Air temperature [K]': [new_entry.get("Air temperature [K]", 0)],
            'Process temperature [K]': [new_entry.get("Process temperature [K]", 0)],
            'Rotational speed [rpm]': [new_entry.get("Rotational speed [rpm]", 0)],
            'Torque [Nm]': [new_entry.get("Torque [Nm]", 0)],
            'Tool wear [min]': [new_entry.get("Tool wear [min]", 0)],
        }

        # Make the API request
        r = requests.post(url, json=new_sample_json)

        # Parse the JSON response
        prediction_result = r.json()

        # Insert the prediction results into the MongoDB collection
        post = {
            "_id": original_id,
            "timestamp": original_timestamp,
            "status": prediction_result.get("Predicted Target", "N/A"),
            "fType": prediction_result.get("Predicted Failure Type", "N/A")
        }
        collection_shaft_status.insert_one(post)

        print(f"Inserted document with ID: {post['_id']}")
        print(r.json())

    except Exception as e:
        print(f'Error processing new entry: {str(e)}')

def watch_database():
    with collection_shaft_readings.watch(full_document='updateLookup') as stream:
        for change in stream:
            new_entry = change['fullDocument']
            process_new_entry(new_entry)

if __name__ == "__main__":
    # Run the watch_database function in a separate thread
    watch_thread = Thread(target=watch_database)
    watch_thread.start()
