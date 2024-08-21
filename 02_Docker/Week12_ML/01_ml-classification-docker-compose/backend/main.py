# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd
from sklearn.datasets import load_iris, load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

app = FastAPI()

# Dictionary to store trained models
models = {}

# Load example datasets
datasets = {
    "iris": load_iris(as_frame=True),
    "wine": load_wine(as_frame=True)
}

class TrainRequest(BaseModel):
    dataset_name: str
    model_name: str

class PredictRequest(BaseModel):
    model_name: str
    test_data: List[List[float]]

@app.post("/train/")
async def train_model(request: TrainRequest):
    if request.dataset_name not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if request.model_name not in ["random_forest", "gradient_boosting"]:
        raise HTTPException(status_code=400, detail="Invalid model name")

    # Load dataset
    data = datasets[request.dataset_name]
    X = data.data
    y = data.target

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Select model
    if request.model_name == "random_forest":
        model = RandomForestClassifier()
    elif request.model_name == "gradient_boosting":
        model = GradientBoostingClassifier()

    # Train model
    model.fit(X_train, y_train)

    # Save the model
    models[request.model_name] = model

    return {"message": f"{request.model_name} trained on {request.dataset_name} dataset"}

@app.post("/predict/")
async def predict(request: PredictRequest):
    if request.model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")

    model = models[request.model_name]
    predictions = model.predict(request.test_data)
    return {"predictions": predictions.tolist()}
