"""
train.py   Machine Failure Classification Training Pipeline
Run from project root:  python train.py
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from imblearn.over_sampling import SMOTE

from preprocess import MachineFailurePreprocessor

#  Paths  #
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT_DIR, "data", "predictive_maintenance.csv")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "model.joblib")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")
METADATA_PATH = os.path.join(MODELS_DIR, "metadata.json")


#  Banner  #
def _banner(text: str, width: int = 60):
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def train():
    os.makedirs(MODELS_DIR, exist_ok=True)
    _banner("Machine Failure Classification - Training Pipeline")

    #  1. Load Data  #
    print("\n1/7 Loading data ...")
    df = pd.read_csv(DATA_PATH)
    print(f"      Shape   : {df.shape}")
    print(f"      Columns : {df.columns.tolist()}")
    class_dist = df["Target"].value_counts().to_dict()
    print(f"      Classes : {class_dist}  (0=No Failure, 1=Failure)")

    #  2. Preprocess  #
    print("\n2/7 Preprocessing ...")
    preprocessor = MachineFailurePreprocessor()
    X, y = preprocessor.fit_transform(df)
    print(f"      Feature matrix shape : {X.shape}")
    print(f"      Features             : {preprocessor.feature_columns}")

    #  3. Train / Test Split  #
    print("\n3/7 Splitting dataset (80/20, stratified) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"      Train : {X_train.shape[0]} samples")
    print(f"      Test  : {X_test.shape[0]} samples")

    #  4. Handle Imbalance  #
    # We use XGBoost's native scale_pos_weight instead of SMOTE for better stability
    print("\n4/7 Calculating class weights for imbalance handling ...")
    counts = np.bincount(y_train)
    pos_weight = counts[0] / counts[1]
    print(f"      Negative samples : {counts[0]}")
    print(f"      Positive samples : {counts[1]}")
    print(f"      Suggested scale_pos_weight : {pos_weight:.2f}")

    #  5. Train Model  #
    print(f"\n5/7 Training XGBoost Classifier (pos_weight={pos_weight:.1f}) ...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        verbosity=1,
        objective="binary:logistic",
        scale_pos_weight=pos_weight,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print("      Training complete OK")

    #    6. Evaluate  #
    print("\n6/7 Evaluating on test set ...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n      Accuracy  : {accuracy:.4f}  ({accuracy * 100:.2f} %)")
    print(f"      ROC AUC   : {roc_auc:.4f}")
    print(f"\n      Confusion Matrix:")
    print(f"        TN={cm[0, 0]}  FP={cm[0, 1]}")
    print(f"        FN={cm[1, 0]}  TP={cm[1, 1]}")
    print(f"\n      Classification Report:")
    print(
        classification_report(
            y_test, y_pred, target_names=["No Failure", "Failure"]
        )
    )

    # Feature importance
    importances = dict(
        zip(
            preprocessor.feature_columns,
            model.feature_importances_.tolist(),
        )
    )
    sorted_imp = dict(
        sorted(importances.items(), key=lambda x: x[1], reverse=True)
    )
    print("      Top Feature Importances:")
    for feat, imp in sorted_imp.items():
        bar = "#" * int(imp * 40)
        print(f"        {feat:<35} {bar} {imp:.4f}")

    #    7. Save    #
    print("\n7/7 Saving model artefacts ...")
    joblib.dump(model, MODEL_PATH)
    print(f"      OK Model         to  {MODEL_PATH}")

    preprocessor.save(PREPROCESSOR_PATH)

    metadata = {
        "model_type": "XGBClassifier",
        "n_estimators": 300,
        "max_depth": 6,
        "learning_rate": 0.1,
        "scale_pos_weight": round(float(pos_weight), 2),
        "accuracy": round(float(accuracy), 6),
        "roc_auc": round(float(roc_auc), 6),
        "feature_columns": preprocessor.feature_columns,
        "feature_importances": sorted_imp,
        "training_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "confusion_matrix": cm.tolist(),
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"      OK Metadata      to  {METADATA_PATH}")

    _banner("Training complete - model ready for deployment!")
    return model, preprocessor, metadata


if __name__ == "__main__":
    train()
