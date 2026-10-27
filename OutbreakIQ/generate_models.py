"""
generate_models.py — Run this ONCE to create mock .pkl model files.

Usage:
    cd health-guard-main/backend
    python generate_models.py

This creates:
    model/risk_model.pkl
    model/label_encoder.pkl
    model/feature_cols.pkl

These are placeholder models trained on synthetic data.
Replace them with your real trained models when available.
"""

import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

FEATURE_COLS = [
    'tempmax', 'tempmin', 'temp', 'humidity', 'precip', 'precipprob',
    'windspeed', 'cloudcover', 'visibility', 'uvindex', 'dew', 'sealevelpressure'
]

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

np.random.seed(42)
n = 600

# Synthetic feature matrix
X = np.column_stack([
    np.random.uniform(28, 42, n),   # tempmax
    np.random.uniform(20, 32, n),   # tempmin
    np.random.uniform(24, 37, n),   # temp
    np.random.uniform(40, 100, n),  # humidity
    np.random.uniform(0, 80, n),    # precip
    np.random.uniform(0, 100, n),   # precipprob
    np.random.uniform(5, 30, n),    # windspeed
    np.random.uniform(10, 100, n),  # cloudcover
    np.random.uniform(1, 10, n),    # visibility
    np.random.uniform(3, 12, n),    # uvindex
    np.random.uniform(15, 30, n),   # dew
    np.random.uniform(995, 1020, n),# sealevelpressure
])

# Synthetic labels based on simple rules
def label(row):
    score = 0
    if row[3] > 85: score += 3   # humidity
    elif row[3] > 70: score += 1
    if row[4] > 30: score += 2   # precip
    elif row[4] > 10: score += 1
    if row[2] > 35: score += 2   # temp
    elif row[2] > 30: score += 1
    if row[5] > 80: score += 2   # precipprob
    if score >= 6: return "High"
    if score >= 3: return "Medium"
    return "Low"

y_labels = np.array([label(row) for row in X])

le = LabelEncoder()
y_encoded = le.fit_transform(y_labels)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y_encoded)

joblib.dump(clf, os.path.join(MODEL_DIR, "risk_model.pkl"))
joblib.dump(le,  os.path.join(MODEL_DIR, "label_encoder.pkl"))
joblib.dump(FEATURE_COLS, os.path.join(MODEL_DIR, "feature_cols.pkl"))

print("✅ Model files created in:", MODEL_DIR)
print("   risk_model.pkl")
print("   label_encoder.pkl")
print("   feature_cols.pkl")
print("\nClasses:", list(le.classes_))
print("Replace with your real .pkl files for production use.")
