"""Train the crop recommendation classifier used by the backend.

The model is a RandomForestClassifier that predicts a crop label (a string such
as "rice" or "maize") from the six soil/environment values the system can
actually measure:

    nitrogen, phosphorus, potassium, ph, temperature, humidity

Soil moisture is deliberately not a model feature: the training dataset records
rainfall (mm) rather than soil moisture (%), so the backend uses the Arduino
soil moisture reading for irrigation advice instead of for the prediction.

Run from this directory:  python train_crop_model.py
"""

import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(HERE, 'crop_recommendation_dataset.csv')
MODEL_PATH = os.path.join(HERE, 'crop_model.pkl')

# Order must match MODEL_FEATURES in backend/crop_recommendation.py
FEATURE_COLUMNS = ['N', 'P', 'K', 'ph', 'temperature', 'humidity']
TARGET_COLUMN = 'label'


def main():
    df = pd.read_csv(DATASET_PATH)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100, min_samples_leaf=3, random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"Crops: {len(model.classes_)} -> {list(model.classes_)}")
    print(f"Test accuracy: {accuracy_score(y_test, preds):.4f}")
    print(classification_report(y_test, preds))

    # Refit on the full dataset before saving
    model.fit(X, y)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == '__main__':
    main()
