import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyATz2SrNzjSCVm5PEuPT-WnoeElIwE8TWs"

from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.genai import types
import pandas as pd
import asyncio, json


from pydantic import BaseModel

APP_NAME = "data_pipeline"
session_service = InMemorySessionService()


class RepairSchema(BaseModel):
    repair_summary: str
    repair_code: str


async def run_repair(diagnosis):

    try:
        await session_service.create_session(
        session_id="repair-session",
        user_id="vidhi",
        app_name="data_pipeline"
    )
    except AlreadyExistsError:
        pass

    prompt = f"""
You are a repair agent.

Fix the error in the pipeline based on this diagnosis:

{diagnosis}

Return valid JSON:
{{
  "repair_summary": "...",
  "repair_code": "python code that modifies df IN-PLACE. NO reassignment of df = ... do not try to add new columns"
}}
"""

    agent = LlmAgent(
        name="RepairAgent",
        model="gemini-2.5-flash",
        instruction="Generate robust pandas repair code",
        output_schema=RepairSchema
    )

    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    events = runner.run_async(
        user_id="vidhi",
        session_id="repair-session",
        new_message=message
    )

    async for ev in events:
        if ev.content and ev.content.parts:
            raw = ev.content.parts[0].text

            try:
                result = json.loads(raw)
            except:
                print("RAW:", raw)
                return {"repair_summary": "failed", "repair_code": ""}

            # ------- APPLY REPAIR TO DATAFRAME -------
            
            df = pd.read_csv("data_check.csv")
            try:
                
                exec(result["repair_code"], {"df": df, "pd": pd})
                df.to_csv("data_check.csv", index=False)
                
            except Exception as e:
                print("Repair execution error:", e)

            return result

    return {"repair_summary": "no output", "repair_code": ""}
