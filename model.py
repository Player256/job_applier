from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class JobPost(BaseModel):
    title: str
    company: str
    location: str
    date_applied: datetime
    application_status: Literal["applied", "interviewing", "rejected", "offer_received "] = "applied"

class Jobs(BaseModel):
    jobs: list[JobPost]