import sqlite3
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
import requests
import os
from flask import send_from_directory

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
app.secret_key = "your_secret_key"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# Initialize DB
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Load and train model
df = pd.read_csv("Fertilizer Prediction.csv")
X = df.drop('Fertilizer_Name', axis=1)
y = df['Fertilizer_Name']

categorical_cols = X.select_dtypes(include='object').columns
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = pd.DataFrame(encoder.fit_transform(X[categorical_cols]))
X_encoded.columns = encoder.get_feature_names_out(categorical_cols)
X_final = pd.concat([X_encoded, X.drop(columns=categorical_cols).reset_index(drop=True)], axis=1)

model = RandomForestClassifier()
model.fit(X_final, y)

joblib.dump(model, 'fertilizer_model.pkl')
joblib.dump(encoder, 'encoder.pkl')
joblib.dump(categorical_cols.tolist(), 'categorical_cols.pkl')
joblib.dump(X_final.columns.tolist(), 'model_columns.pkl')

@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

# Serve other routes to React (React Router support)
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

# Routes
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

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   (username, email, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        zip_code = data['zip']
        api_key = "e0788c1a78dd449313c5853a735034bf"

        weather_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code},in&appid={api_key}"
        weather_resp = requests.get(weather_url)

        if weather_resp.status_code != 200:
            return jsonify({'error': 'Weather API error', 'details': weather_resp.text})

        weather_data = weather_resp.json()
        temperature = round(weather_data['main']['temp'] - 273.15, 2)
        humidity = weather_data['main']['humidity']

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

        model = joblib.load('fertilizer_model.pkl')
        encoder = joblib.load('encoder.pkl')
        categorical_cols = joblib.load('categorical_cols.pkl')
        model_columns = joblib.load('model_columns.pkl')

        user_encoded = pd.DataFrame(encoder.transform(user_input[categorical_cols]))
        user_encoded.columns = encoder.get_feature_names_out(categorical_cols)

        user_final = pd.concat([user_encoded, user_input.drop(columns=categorical_cols)], axis=1)
        user_final = user_final.reindex(columns=model_columns, fill_value=0)

        prediction = model.predict(user_final)[0]

        return jsonify({'fertilizer_recommendation': prediction})

    except Exception as e:
        return jsonify({'error': str(e)})

# Run the app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
