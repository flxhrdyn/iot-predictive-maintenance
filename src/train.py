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
from sklearn.ensemble import RandomForestClassifier
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
    print(f"      Train : {X_train.shape0} samples")
    print(f"      Test  : {X_test.shape0} samples")

    #  4. SMOTE  #
    print("\n4/7 Applying SMOTE to balance training classes ...")
    before = dict(zip(*np.unique(y_train, return_counts=True)))
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    after = dict(zip(*np.unique(y_train_res, return_counts=True)))
    print(f"      Before SMOTE : {before}")
    print(f"      After  SMOTE : {after}")

    #  5. Train Model  #
    print("\n5/7 Training Random Forest Classifier ...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_res, y_train_res)
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
    print(f"        TN={cm0,0}  FP={cm0,1}")
    print(f"        FN={cm1,0}  TP={cm1,1}")
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
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "max_depth": 12,
        "accuracy": round(float(accuracy), 6),
        "roc_auc": round(float(roc_auc), 6),
        "feature_columns": preprocessor.feature_columns,
        "feature_importances": sorted_imp,
        "training_samples": int(X_train_res.shape[0]),
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
