# Diagnostic.py
import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")

from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.genai import types
import asyncio, json
from pydantic import BaseModel
from typing import List

class DiagnosisSchema(BaseModel):
    diagnosis: str
    severity: str
    suggested_corrections: List[str]

session_service = InMemorySessionService()

async def run_diagnostic(error_payload):

    try:
        await session_service.create_session(
        session_id="diagnostic-session",
        user_id="vidhi",
        app_name="data_pipeline"
    )
    except AlreadyExistsError:
        pass

    prompt = f"""
You are a data diagnostics expert.

Error: {error_payload['error']}
Context: {error_payload.get('context', {})}

Return JSON:
{{
 "diagnosis": "...",
 "severity": "low|medium|high",
 "suggested_corrections": ["...", "..."]
}}
"""

    agent = LlmAgent(
        name="DiagnosticAgent",
        model="gemini-2.5-flash",
        api_key=api_key,
        instruction="Diagnose data errors.",
        output_schema=DiagnosisSchema,
    )

    runner = Runner(
        agent=agent,
        app_name="data_pipeline",
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    events = runner.run_async(
        user_id="vidhi",
        session_id="diagnostic-session",
        new_message=message
    )

    async for ev in events:
        if ev.content and ev.content.parts:
            text = ev.content.parts[0].text
            try:
                return json.loads(text)
            except:
                return {"diagnosis": "Failed to parse", "severity": "high", "suggested_corrections": []}

    return {"diagnosis": "Unknown error", "severity": "high", "suggested_corrections": []}
