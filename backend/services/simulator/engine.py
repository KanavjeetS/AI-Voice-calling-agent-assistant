from typing import Dict, List

from core.agent.engine import loan_voice_agent
from models.schemas import Lead, SimulatorRequest, SimulatorResponse, SimulatorTurn


SCENARIOS: Dict[str, List[str]] = {
    "interested": [
        "Hello, yes I applied for the loan.",
        "Am I eligible with a salary of 60 thousand?",
        "What will be the EMI for five years?",
        "I can send the salary slip today.",
        "Please connect me with an agent.",
    ],
    "hindi": [
        "Namaste, haan maine loan apply kiya tha.",
        "Meri salary 55 hazaar hai, kya eligible hoon?",
        "EMI kitni hogi?",
        "PAN card kal bhej dunga.",
        "Kal 4 pm callback kara dijiye.",
    ],
    "angry": [
        "Why are you calling me again?",
        "Stop calling. I am angry about this.",
        "Connect me to a senior person now.",
    ],
    "confused": [
        "I do not understand the document requirement.",
        "Can you explain the interest rate?",
        "Maybe call me tomorrow.",
    ],
}


async def run_simulation(request: SimulatorRequest) -> SimulatorResponse:
    utterances = SCENARIOS.get(request.scenario, SCENARIOS["interested"])[: request.turns]
    lead = Lead(
        id="sim_lead",
        name="Simulation Customer",
        phone_number="+910000000000",
        loan_amount=1_800_000 if request.scenario == "interested" else 500_000,
        language_hint="hindi" if request.language == "hindi" else "english",
        missing_fields=["salary_slip", "bank_statement"],
    )
    turns: list[SimulatorTurn] = []
    final_status = lead.status
    for utterance in utterances:
        reply = await loan_voice_agent.generate_reply(lead, utterance)
        final_status = reply.lead_status
        turns.append(SimulatorTurn(customer=utterance, agent=reply))
    return SimulatorResponse(
        scenario=request.scenario,
        language=request.language,
        turns=turns,
        final_status=final_status,
    )
