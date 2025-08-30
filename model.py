from pydantic import BaseModel
from datetime import date
from typing import Literal, Optional

class JobPost(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None
    date_applied: date
    application_status: Literal["applied", "interviewing", "rejected", "offer_received "] = "applied"

class Jobs(BaseModel):
    jobs: list[JobPost]