from google.adk.agents import Agent
from DataQualityAgent.dq_agent import load_and_check_data_tool

def validate_cleaned_data_tool(file_path: str):
    result = load_and_check_data_tool(file_path)

    if result["status"] == "ok":
        return {
            "status": "passed",
            "message": "All checks passed after cleaning.",
            "details": result
        }
    else:
        return {
            "status": "failed",
            "message": "Some checks still failing.",
            "details": result
        }

validation_agent = Agent(
    name="validation_agent",
    instruction="Validate cleaned data using validate_cleaned_data_tool.",
    tools=[validate_cleaned_data_tool]
)
