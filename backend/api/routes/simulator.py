from fastapi import APIRouter

from models.schemas import SimulatorRequest, SimulatorResponse
from services.simulator.engine import run_simulation

router = APIRouter(prefix="/api/v1/simulator", tags=["simulator"])


@router.post("/run", response_model=SimulatorResponse)
async def simulate_call(payload: SimulatorRequest) -> SimulatorResponse:
    return await run_simulation(payload)
