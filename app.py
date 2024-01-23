import numpy as np
from flask import Flask, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# Load the trained model
with open('modelfinal 2.0.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)

# Load the fitted ColumnTransformer
with open('column_transformer 2.0.pkl', 'rb') as ct_file:
    fitted_ct = pickle.load(ct_file)

# Load the LabelEncoder for 'Failure Type'
with open('label_encoder.pkl', 'rb') as le_file:
    label_encoder = pickle.load(le_file)

@app.route('/predict_api', methods=['POST'])
def predict_api():
    '''
    For direct API calls through request
    '''
    try:
        # Extract input data from the JSON request
        data = request.get_json(force=True)
        
        # Create a DataFrame from the input data
        new_sample = pd.DataFrame(data)

        # Transform the new sample using the loaded ColumnTransformer
        new_sample_transformed = fitted_ct.transform(new_sample)

        # Make predictions using the loaded model
        predictions = loaded_model.predict(new_sample_transformed)

        # Decode the predicted 'Failure Type' using the LabelEncoder
        predicted_failure_type = label_encoder.inverse_transform(predictions[:, 1])

        # Extract the first element from the lists
        predicted_target = predictions[:, 0][0]
        predicted_failure_type = predicted_failure_type[0]

        # Map predicted_target to "ok" or "possible failure"
        predicted_target_str = "ok" if predicted_target == 0 else "possible failure"

        # Prepare the response with strings instead of lists
        response = {
            'Predicted Target': predicted_target_str,
            'Predicted Failure Type': predicted_failure_type
        }

        # Return the prediction as JSON response
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
