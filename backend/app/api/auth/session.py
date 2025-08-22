



from pydantic import BaseModel


class SessionPayload(BaseModel):
    user_id: str
    session_id: str
    created_at: int
    last_seen: int = -1
    max_age_at: int 
    ip_address: str | None = None
    user_agent: str | None = None




