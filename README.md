
# 🌾 Fertilizer Recommendation System

This is a full-stack web application that recommends the best type of fertilizer based on input factors such as crop name, soil type, season, area, and quantity. It combines a **React frontend**, **Flask backend**, and a **machine learning model** trained on agricultural data.



## 📌 Features

- 🔍 Predicts suitable fertilizers like Urea, DAP, Compost, NPK, etc.
- 🌐 User-friendly interface built with **React (Vite)**
- 🧠 Backend built using **Flask** + **ML model** (RandomForest)
- ☁️ Weather integration via **OpenWeatherMap API**
- 🗂 Handles dynamic input: crop, soil, season, area, and quantity


## 🖥️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React, Tailwind CSS               |
| Backend    | Flask, Python                     |
| ML Model   | RandomForest (sklearn)            |
| API        | OpenWeatherMap (for weather data) |
| Deployment | (Optional) GitHub Pages/Render    |

---

## 🚀 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Nidhi-dorid/MinorProject2025.git
cd MinorProject2025
````

### 2. Backend Setup (Flask)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup (React)

```bash
cd ../frontend
npm install
npm run dev
```

---

 Machine Learning Model

* **Algorithm:** RandomForestClassifier
* **Input Features:** Crop Name, Season, Soil Type, Area, Quantity
* **Output:** Fertilizer Type
* Model is trained using manually created or real datasets (CSV)

---

 Folder Structure

```
MinorProject2025/
│
├── backend/              # Flask server & ML model
│   ├── app.py
│   ├── model.pkl
│   └── ...
│
├── frontend/             # React frontend
│   ├── src/
│   ├── public/
│   └── ...
│
├── requirements.txt
├── README.md
└── .gitignore
```


