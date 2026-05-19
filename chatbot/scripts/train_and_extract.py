import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from pypdf import PdfReader

# Paths
CSV_PATH = 'diabetic_data.csv'
PDF_PATH = 'description.pdf'
MODEL_PATH = 'backend/data/diabetes_model.pkl'
KNOWLEDGE_PATH = 'backend/data/knowledge.txt'
ENCODER_PATH = 'backend/data/encoders.pkl'

def extract_pdf_knowledge():
    print(f"Extracting knowledge from {PDF_PATH}...")
    if not os.path.exists(PDF_PATH):
        print("PDF not found.")
        return

    reader = PdfReader(PDF_PATH)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    with open(KNOWLEDGE_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Knowledge saved to {KNOWLEDGE_PATH}")

def train_model():
    print(f"Training model from {CSV_PATH}...")
    if not os.path.exists(CSV_PATH):
        print("CSV not found.")
        return

    # Load data
    df = pd.read_csv(CSV_PATH)

    # Simple preprocessing
    # Target: readmitted (convert to binary: 1 if <30 or >30, 0 if NO)
    df['readmitted_binary'] = df['readmitted'].apply(lambda x: 1 if x != 'NO' else 0)

    # Features selection (sample for simplicity)
    features = [
        'age', 'time_in_hospital', 'num_lab_procedures',
        'num_medications', 'number_diagnoses', 'insulin',
        'change', 'diabetesMed'
    ]
    X = df[features].copy()
    y = df['readmitted_binary']

    # Encode categorical features
    encoders = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=20, max_depth=10, random_state=42
    )
    model.fit(X_train, y_train)

    print(f"Model accuracy: {model.score(X_test, y_test):.2f}")

    # Save model and encoders
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(encoders, f)

    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    os.makedirs('backend/data', exist_ok=True)
    extract_pdf_knowledge()
    train_model()
