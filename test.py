import requests

# Define the URL for making API requests
url = 'http://localhost:5000/predict_api'

# Make a POST request with JSON data
new_sample_json = {
    'Type': ['L'],
    'Air temperature [K]': [290],
    'Process temperature [K]': [300],
    'Rotational speed [rpm]': [2221],
    'Torque [Nm]': [4],
    'Tool wear [min]': [13],
}

r = requests.post(url, json=new_sample_json)

# Print the JSON response
print(r.json())
