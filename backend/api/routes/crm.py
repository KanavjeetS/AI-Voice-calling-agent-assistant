from fastapi import APIRouter, HTTPException

from models.schemas import Lead, LeadStatus
from services.crm.store import crm_store

router = APIRouter(prefix="/api/v1/crm", tags=["crm"])


@router.get("/leads", response_model=list[Lead])
async def list_leads() -> list[Lead]:
    return await crm_store.list_leads()


@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str) -> Lead:
    lead = await crm_store.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/leads/{lead_id}/status", response_model=Lead)
async def update_lead_status(lead_id: str, status: LeadStatus) -> Lead:
    await crm_store.update_lead_status(lead_id, status)
    lead = await crm_store.get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
