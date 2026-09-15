"""Shared feature engineering used by the Titanic notebook and app."""

from __future__ import annotations

import pandas as pd


RAW_INPUT_COLUMNS = [
    "Pclass",
    "Sex",
    "Age",
    "SibSp",
    "Parch",
    "Fare",
    "Embarked",
]

NUMERIC_FEATURES = [
    "Age",
    "SibSp",
    "Parch",
    "Fare",
    "FamilySize",
    "IsAlone",
]

CATEGORICAL_FEATURES = [
    "Pclass",
    "Sex",
    "Embarked",
]

MODEL_FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create deterministic row-wise features without fitting on the dataset."""
    missing = [column for column in RAW_INPUT_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"필수 Titanic 컬럼이 없습니다: {missing}")

    result = df.copy()

    for column in ["Pclass", "Age", "SibSp", "Parch", "Fare"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    for column in ["Sex", "Embarked"]:
        result[column] = result[column].astype("string").str.strip()

    result["FamilySize"] = result["SibSp"] + result["Parch"] + 1
    result["IsAlone"] = (result["FamilySize"] == 1).astype(int)

    return result
