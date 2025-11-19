# memory/test_memory.py
from qdrant_memory import upsert_incident, search_similar
import uuid

if __name__ == "__main__":
    nid = str(uuid.uuid4())
    upsert_incident(nid, "Test incident: missing column age in batch", {"pipeline":"test","batch":"b1"})
    print("Inserted test incident:", nid)
    hits = search_similar("missing column age")
    print("Search hits:", hits)
