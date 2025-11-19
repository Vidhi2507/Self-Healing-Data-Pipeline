# dq_agent/server.py
from fastapi import FastAPI
from pydantic import BaseModel
from DataQualityAgent.dq_agent import load_and_check_data_tool

app = FastAPI(title="Data Quality Agent API")

class DQRequest(BaseModel):
    file_path: str

@app.post("/check", summary="Check CSV data quality")
def check_data(req: DQRequest):
    """
    Endpoint to run the Data Quality Agent tool on a CSV file.
    Returns a JSON with missing columns, null values, dtype errors, and summary.
    """
    result = load_and_check_data_tool(req.file_path)
    print(result)
    return result