import pandas as pd
import os
from typing import Dict, Any
from google.adk.agents import Agent

def auto_fix_data_tool(file_path: str) -> Dict[str, Any]:

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }

    df = pd.read_csv(file_path)
    actions = []

    # Required fields with defaults
    required_cols = {"id": -1, "name": "unknown", "age": 0}

    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default
            actions.append(f"Added missing column {col}")

    # Fix nulls
    for col in df.columns:
        if df[col].isna().sum() > 0:
            fill_value = df[col].median() if df[col].dtype != 'object' else "unknown"
            df[col].fillna(fill_value, inplace=True)
            actions.append(f"Filled nulls in {col}")

    # Fix age dtype
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
        actions.append("Converted age to numeric")

    cleaned_path = file_path.replace(".csv", "_cleaned.csv")
    df.to_csv(cleaned_path, index=False)

    return {
        "status": "fixed",
        "actions": actions,
        "cleaned_file": cleaned_path
    }

clean_agent = Agent(
    name="data_cleaning_agent",
    instruction="Fix missing columns, nulls, and datatype issues using auto_fix_data_tool.",
    tools=[auto_fix_data_tool]
)
