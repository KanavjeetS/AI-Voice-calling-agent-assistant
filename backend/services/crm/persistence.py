from typing import Any, Dict

from models.schemas import CallRecord
from services.crm.store import crm_store

async def save_call_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {"saved": True, "summary": summary}


async def save_call_record(record: CallRecord) -> CallRecord:
    return await crm_store.save_call(record)
