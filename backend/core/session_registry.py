from typing import Dict, Optional

from core.call_session import CallSession


class SessionRegistry:
    def __init__(self) -> None:
        self._sessions: Dict[str, CallSession] = {}

    async def create(self, call_sid: str, customer_phone: str | None = None) -> CallSession:
        session = CallSession(call_sid=call_sid, customer_phone=customer_phone)
        self._sessions[call_sid] = session
        return session

    async def get(self, call_sid: str) -> Optional[CallSession]:
        return self._sessions.get(call_sid)

    async def remove(self, call_sid: str) -> None:
        self._sessions.pop(call_sid, None)


session_registry = SessionRegistry()
