# memory/qdrant_memory.py
import os
import uuid
from typing import List, Dict, Any
from xmlrpc import client

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.models import PointStruct

# google-genai (Gemini)
from google import genai
from dotenv import load_dotenv
load_dotenv()

#diagnostic agent import for embedding
from DiagnosticAgent import run_diagnostic

# Configure Gemini (google-genai)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Collection config
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME")
VECTOR_SIZE = 768  
def get_qdrant_client() -> QdrantClient:
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise EnvironmentError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, check_compatibility=False)

def ensure_collection(vector_size: int = VECTOR_SIZE):
    client = get_qdrant_client()
    try:
        client.get_collection(collection_name=QDRANT_COLLECTION)
    except Exception:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
        )

def embed_text_gemini(text: str) -> List[float]:
    if not GOOGLE_API_KEY:
        raise EnvironmentError("GOOGLE_API_KEY not set in .env")

    # call genai embed API
    client = genai.Client(api_key=GOOGLE_API_KEY)

    resp = client.models.embed_content(model='text-embedding-004',contents=text)
    
    # API may return structure like {'embedding': [...]} or a dict with 'data' - adjust if needed
    #print(resp)
    embedding = resp.embeddings[0].values
    if not embedding:
        raise ValueError("Embedding response did not contain 'embedding'. Response: " + str(resp))
    return embedding

def upsert_incident(incident_id: str, text_summary: str, metadata: Dict[str, Any]):
    client = get_qdrant_client()
    ensure_collection()
    # get embedding
    vec = embed_text_gemini(text_summary)
    point = PointStruct(id=incident_id, vector=vec, payload={"diagnosis": text_summary, "severity": metadata})
    client.upsert(collection_name=QDRANT_COLLECTION, points=[point])

# def search_similar(text_query: str, limit: int = 3):
#     client = get_qdrant_client()
#     ensure_collection()
#     q_vec = embed_text_gemini(text_query)
#     hits = client.query_points(collection_name=QDRANT_COLLECTION, query=q_vec, limit=limit)
    
#     print("----")
#     points = hits.points
#     results = []
#     for h in points:
#         #print(h)
#         results.append({"id": h.id, "score": h.score, "payload": h.payload})
        
#     return results

if __name__ == "__main__":
    print(f"Upserted incident in Qdrant Memory")
