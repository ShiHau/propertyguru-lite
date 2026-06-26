from pydantic import BaseModel


class RejectedResponse(BaseModel):
    status: str = "rejected"
    reason: str
    message: str
