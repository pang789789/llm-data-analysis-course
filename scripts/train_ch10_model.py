from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "ch10_cancel_model.joblib"

FEATURES = [
    "age",
    "gender",
    "city",
    "payment_method",
    "item_count",
    "total_quantity",
    "order_amount",
]
NUMERIC_FEATURES = ["age", "item_count", "total_quantity", "order_amount"]
CATEGORICAL_FEATURES = ["gender", "city", "payment_method"]


def load_training_data() -> pd.DataFrame:
    orders = pd.read_csv(RAW_DIR / "orders.csv")
    items = pd.read_csv(RAW_DIR / "order_items.csv")
    customers = pd.read_csv(RAW_DIR / "customers.csv")

    orders = orders.loc[orders["order_status"].isin(["completed", "cancelled"])].copy()
    orders["is_cancelled"] = (orders["order_status"] == "cancelled").astype(int)

    items["line_total"] = items["quantity"] * items["unit_price"]
    order_features = items.groupby("order_id", as_index=False).agg(
        item_count=("product_id", "nunique"),
        total_quantity=("quantity", "sum"),
        order_amount=("line_total", "sum"),
    )

    data = orders.merge(order_features, on="order_id", how="inner", validate="1:1")
    data = data.merge(
        customers[["customer_id", "age", "gender", "city"]],
        on="customer_id",
        how="inner",
        validate="m:1",
    )
    required = FEATURES + ["is_cancelled"]
    if data[required].isna().any().any():
        raise ValueError("학습 데이터의 필수 열에 결측치가 있습니다.")
    return data


def make_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ]
    )


def train_and_save() -> Path:
    data = load_training_data()
    X = data[FEATURES]
    y = data["is_cancelled"]

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.25,
        random_state=42,
        stratify=y_train_val,
    )

    candidates = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Random Forest": RandomForestClassifier(
            random_state=42, n_estimators=300, min_samples_leaf=2
        ),
    }
    validation_rows = []
    fitted = {}
    for name, estimator in candidates.items():
        pipeline = Pipeline(
            [("preprocessor", make_preprocessor()), ("classifier", estimator)]
        )
        pipeline.fit(X_train, y_train)
        probabilities = pipeline.predict_proba(X_val)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        validation_rows.append(
            {
                "model": name,
                "f1": f1_score(y_val, predictions, zero_division=0),
                "roc_auc": roc_auc_score(y_val, probabilities),
            }
        )
        fitted[name] = pipeline

    validation = pd.DataFrame(validation_rows).sort_values(
        ["f1", "roc_auc"], ascending=False
    )
    selected_name = str(validation.iloc[0]["model"])
    selected = fitted[selected_name]
    val_probabilities = selected.predict_proba(X_val)[:, 1]

    threshold_rows = []
    for threshold in np.arange(0.1, 1.0, 0.05):
        predictions = (val_probabilities >= threshold).astype(int)
        threshold_rows.append(
            {
                "threshold": round(float(threshold), 2),
                "f1": f1_score(y_val, predictions, zero_division=0),
                "recall": recall_score(y_val, predictions, zero_division=0),
            }
        )
    threshold_result = pd.DataFrame(threshold_rows).sort_values(
        ["f1", "recall", "threshold"], ascending=[False, False, True]
    )
    threshold = float(threshold_result.iloc[0]["threshold"])

    final_model = clone(selected)
    final_model.fit(X_train_val, y_train_val)
    test_probabilities = final_model.predict_proba(X_test)[:, 1]
    test_predictions = (test_probabilities >= threshold).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_test, test_predictions)),
        "precision": float(precision_score(y_test, test_predictions, zero_division=0)),
        "recall": float(recall_score(y_test, test_predictions, zero_division=0)),
        "f1": float(f1_score(y_test, test_predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, test_probabilities)),
        "test_size": int(len(y_test)),
    }

    categories = {
        column: sorted(data[column].dropna().astype(str).unique().tolist())
        for column in CATEGORICAL_FEATURES
    }
    ranges = {
        column: {
            "min": float(data[column].min()),
            "max": float(data[column].max()),
            "median": float(data[column].median()),
        }
        for column in NUMERIC_FEATURES
    }
    artifact = {
        "model": final_model,
        "threshold": threshold,
        "model_name": selected_name,
        "features": FEATURES,
        "categories": categories,
        "ranges": ranges,
        "metrics": metrics,
        "training_rows": int(len(data)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f"모델 저장 완료: {MODEL_PATH}")
    print(f"선택 모델: {selected_name}")
    print(f"임계값: {threshold:.2f}")
    print("Final test metrics:", metrics)
    return MODEL_PATH


if __name__ == "__main__":
    train_and_save()
