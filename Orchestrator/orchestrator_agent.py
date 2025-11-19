
from google.adk.agents import Agent
from DataQualityAgent.dq_agent import load_and_check_data_tool
from Repair.main import auto_fix_data_tool
from Validator.Validator import validate_cleaned_data_tool

def run_full_pipeline_tool(file_path: str):
    logs = {}

    # Step 1: Quality Check
    dq_result = load_and_check_data_tool(file_path)
    logs["data_quality"] = dq_result

    # If no issues → done
    if dq_result["status"] == "ok":
        return {"status": "ok", "logs": logs}

    # Step 2: Auto Cleanup
    clean_result = auto_fix_data_tool(file_path)
    logs["cleaning"] = clean_result

    cleaned_file = clean_result["cleaned_file"]

    # Step 3: Validation
    validation_result = validate_cleaned_data_tool(cleaned_file)
    logs["validation"] = validation_result

    if validation_result["status"] == "passed":
        return {"status": "success", "cleaned_file": cleaned_file, "logs": logs}

    return {"status": "failed", "logs": logs}

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instruction="Run data quality check → cleaning → validation using run_full_pipeline_tool.",
    tools=[run_full_pipeline_tool]
)
