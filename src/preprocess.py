\"\"\"
preprocess.py Machine Failure Classification module
This is a reusable preprocessing pipeline that includes Feature Engineering, Winsorizing, Encoding, and Scaling components.
\"\"\"

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, OrdinalEncoder


class MachineFailurePreprocessor:
    \"\"\"
    """
    End to end preprocessing pipeline for Machine Failure Classification

    Applied steps in exact execution order:
      1 Feature Engineering using Temp Diff and Power metrics
      2 Column Selection bypassing ID or leakage columns
      3 Winsorizing using fifth and ninety fifth percentile boundaries
      4 Ordinal Encoding shifting Type L to 0, M to 1, and H to 2
      5 Standard Scaling forcing zero mean and unit variance
    """

    # Columns that must be removed before model training or inference execution
    _DROP_COLS = ["UDI", "Product ID", "Failure Type"]
    _TARGET_COL = "Target"

    # Numerical columns that may contain outliers to winsorise
    _NUMERIC_COLS = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
        "Temp_Diff [K]",
        "Power [W]",
    ]

    def __init__(self):
        self.encoder = OrdinalEncoder(
            categories=[["L", "M", "H"]],
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        )
        self.scaler = StandardScaler()
        self.winsor_bounds: dict = {}
        self.feature_columns: list = []
        self.is_fitted: bool = False

    # Private helpers

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates domain specific engineered features from physical parameters
        """
        df = df.copy()
        df["Temp_Diff [K]"] = (
            df["Process temperature [K]"] - df["Air temperature [K]"]
        )
        
        # Mechanical power in Watts equates to torque times angular velocity
        df["Power [W]"] = (
            df["Torque [Nm]"]
            * df["Rotational speed [rpm]"]
            * (2 * np.pi / 60)
        )
        return df

    def _compute_winsor_bounds(self, df: pd.DataFrame) -> dict:
        """
        Computes the boundary points based on the fifth and ninety fifth percentiles from the raw training dataset
        """
        bounds = {}
        for col in self._NUMERIC_COLS:
            if col not in df.columns:
                continue
            bounds[col] = {
                "lower": df[col].quantile(0.05),
                "upper": df[col].quantile(0.95),
            }
        return bounds

    def _apply_winsorizing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clips dataframe numerical values strictly utilizing precomputed bounding dictates
        """
        df = df.copy()
        for col, b in self.winsor_bounds.items():
            if col in df.columns:
                df[col] = df[col].clip(lower=b["lower"], upper=b["upper"])
        return df

    def _drop_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove leakage or ID columns if present."""
        cols = [c for c in self._DROP_COLS if c in df.columns]
        return df.drop(columns=cols)

    # Public API

    def fit_transform(self, df: pd.DataFrame):
        """
        Fit the pipeline on training data and return X array and y array.
        Call this once on your training DataFrame.
        """
        df = df.copy()

        # Separate target before feature engineering
        y = df[self._TARGET_COL].values if self._TARGET_COL in df.columns else None
        df = df.drop(columns=[self._TARGET_COL], errors="ignore")

        # 1 Remove irrelevant columns
        df = self._drop_columns(df)

        # 2 Feature engineering
        df = self._engineer_features(df)

        # 3 Winsorizing
        self.winsor_bounds = self._compute_winsor_bounds(df)
        df = self._apply_winsorizing(df)

        # 4 Ordinal encode Type
        if "Type" in df.columns:
            df["Type"] = self.encoder.fit_transform(df[["Type"]]).ravel()

        # 5 Record column order important for inference
        self.feature_columns = df.columns.tolist()

        # 6 Scale
        X = self.scaler.fit_transform(df)

        self.is_fitted = True
        return (X, y) if y is not None else X

    def transform(self, data) -> np.ndarray:
        """
        Transform new data using the fitted pipeline.
        Use this at inference time.
        """
        if not self.is_fitted:
            raise RuntimeError(
                "Preprocessor is not fitted. Call fit_transform first."
            )

        # Accept dict or DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise TypeError("Input must be a dict or a pandas DataFrame.")

        # Rename external friendly keys to internal column names
        rename_map = {
            "type": "Type",
            "air_temperature_K": "Air temperature [K]",
            "process_temperature_K": "Process temperature [K]",
            "rotational_speed_rpm": "Rotational speed [rpm]",
            "torque_Nm": "Torque [Nm]",
            "tool_wear_min": "Tool wear [min]",
        }
        df = df.rename(columns=rename_map)

        # Drop ID leakage and target columns
        df = df.drop(columns=self._DROP_COLS + [self._TARGET_COL], errors="ignore")
        # Drop IoT metadata columns not used in the model
        df = df.drop(columns=["device_id"], errors="ignore")

        # Ensure Type is uppercase string for encoder
        if "Type" in df.columns:
            df["Type"] = df["Type"].astype(str).str.upper()

        # Feature engineering
        df = self._engineer_features(df)

        # Winsorizing with training bounds
        df = self._apply_winsorizing(df)

        # Encode Type
        if "Type" in df.columns:
            df["Type"] = self.encoder.transform(df[["Type"]]).ravel()

        # Align columns
        df = df[self.feature_columns]

        return self.scaler.transform(df)

    # Persistence

    def save(self, path: str) -> None:
        """
        Saves the preprocessor object to disk
        """
        joblib.dump(self, path)
        print(f"OK Preprocessor saved to {path}")

    @staticmethod
    def load(path: str) -> "MachineFailurePreprocessor":
        """
        Loads the preprocessor object from disk
        """
        pp = joblib.load(path)
        return pp
