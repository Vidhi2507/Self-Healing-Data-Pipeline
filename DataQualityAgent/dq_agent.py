# dq_agent/agent.py
import pandas as pd
import os
from typing import Dict, Any
from google.adk.agents import Agent

# ===== TOOL: Load & Check Data Quality =====
def load_and_check_data_tool(file_path: str) -> Dict[str, Any]:
    """
    Loads a CSV file and performs basic data quality checks.
    Returns a structured dictionary of issues.
    """

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }

    df = pd.read_csv(file_path)

    issues = {
        "status": "ok",
        "missing_columns": [],
        "null_values": {},
        "dtype_errors": {},
        "summary": ""
    }

    # RULE 1: Required columns
    required_columns = ["id", "name", "age"]
    for col in required_columns:
        if col not in df.columns:
            issues["missing_columns"].append(col)

    # RULE 2: Null value counts
    for col in df.columns:
        nulls = df[col].isna().sum()
        if nulls > 0:
            issues["null_values"][col] = int(nulls)

    # RULE 3: Dtype checks (simple)
    for col in df.columns:
        if df[col].dtype == 'object' and col in ["age"]:
            issues["dtype_errors"][col] = "age should be numeric"

    # Summary message
    summary_parts = []
    if issues["missing_columns"]:
        summary_parts.append(f"Missing columns: {issues['missing_columns']}")
    if issues["null_values"]:
        summary_parts.append(f"Columns with nulls: {issues['null_values']}")
    if issues["dtype_errors"]:
        summary_parts.append(f"Dtype errors: {issues['dtype_errors']}")

    if summary_parts:
        issues["status"] = "error"
        issues["summary"] = "; ".join(summary_parts)
    else:
        issues["summary"] = "Data quality check passed with no issues."

    return issues


# ===== AGENT DEFINITION =====
dq_agent = Agent(
    name="data_quality_agent",
    instruction="""You are the Data Quality Agent.You analyze datasets for missing columns, null values, and datatype issues.Use the tool `load_and_check_data_tool` to inspect the dataset,and return a structured JSON response describing all issues.""",
    tools=[load_and_check_data_tool]
)
