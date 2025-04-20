from flask import Flask, request, jsonify
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import requests
from flask_cors import CORS
  # Enable CORS for all routes

app = Flask(__name__)
CORS(app)


# Load dataset
df = pd.read_csv("Fertilizer Prediction.csv")  

# Prepare data
X = df.drop('Fertilizer_Name', axis=1)
y = df['Fertilizer_Name']

# One-hot encode categorical columns
categorical_cols = X.select_dtypes(include='object').columns
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = pd.DataFrame(encoder.fit_transform(X[categorical_cols]))
X_encoded.columns = encoder.get_feature_names_out(categorical_cols)

# Combine with numerical features
X_final = pd.concat([X_encoded, X.drop(columns=categorical_cols).reset_index(drop=True)], axis=1)

# Train model
model = RandomForestClassifier()
model.fit(X_final, y)

# Save model and encoder
joblib.dump(model, 'fertilizer_model.pkl')
joblib.dump(encoder, 'encoder.pkl')
joblib.dump(categorical_cols.tolist(), 'categorical_cols.pkl')
joblib.dump(X_final.columns.tolist(), 'model_columns.pkl')


@app.route('/')
def home():
    return "Fertilizer Recommendation API is running!"

@app.route('/get-weather', methods=['POST'])
def get_weather():
    try:
        data = request.get_json()
        zip_code = data.get('zip')
        api_key = "e0788c1a78dd449313c5853a735034bf"

        weather_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},in&appid={api_key}"
        weather_resp = requests.get(weather_url)

        if weather_resp.status_code != 200:
            return jsonify({'error': 'Weather API error', 'details': weather_resp.text})

        weather_data = weather_resp.json()
        temperature = round(weather_data['main']['temp'] - 273.15, 2)
        humidity = weather_data['main']['humidity']

        return jsonify({'temperature': temperature, 'humidity': humidity})

    except Exception as e:
        return jsonify({'error': str(e)})





@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()  

    try:
        # Get ZIP code from input
        zip_code = data['zip']
        api_key = "e0788c1a78dd449313c5853a735034bf"  

        # Fetch weather using OpenWeatherMap API
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},in&appid={api_key}"
        weather_resp = requests.get(weather_url)

        if weather_resp.status_code != 200:
            return jsonify({'error': 'Weather API error', 'details': weather_resp.text})

        weather_data = weather_resp.json()
        temperature = round(weather_data['main']['temp'] - 273.15, 2)  # Kelvin to Celsius
        humidity = weather_data['main']['humidity']

        # Construct user input with fetched weather
        user_input = pd.DataFrame([{
            'Soil_Type': data['Soil_Type'],
            'Crop_Type': data['Crop_Type'],
            'Temperature': temperature,
            'Humidity': humidity,
            'Nitrogen': data['nitrogen'],
            'Phosphorous': data['phosphorous'],
            'Potassium': data['potassium'],
            'Moisture': data['moisture']
        }])

        # Load model components
        model = joblib.load('fertilizer_model.pkl')
        encoder = joblib.load('encoder.pkl')
        categorical_cols = joblib.load('categorical_cols.pkl')
        model_columns = joblib.load('model_columns.pkl')

        # Encode input
        user_encoded = pd.DataFrame(encoder.transform(user_input[categorical_cols]))
        user_encoded.columns = encoder.get_feature_names_out(categorical_cols)

        user_final = pd.concat([user_encoded, user_input.drop(columns=categorical_cols)], axis=1)
        user_final = user_final.reindex(columns=model_columns, fill_value=0)

        # Predict
        prediction = model.predict(user_final)[0]

        return jsonify({
            'fertilizer_recommendation': prediction,
        })

    except Exception as e:
        return jsonify({'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)


