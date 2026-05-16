from typing import Dict

import httpx

from config.settings import settings


async def dispatch_hot_lead_alert(payload: Dict[str, object]) -> bool:
    if not settings.SLACK_WEBHOOK_URL:
        return False
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            settings.SLACK_WEBHOOK_URL,
            json={
                "channel": settings.SLACK_HOT_LEAD_CHANNEL,
                "text": f"Hot loan lead detected: {payload}",
            },
        )
        response.raise_for_status()
    return True
