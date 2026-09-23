from datetime import date, datetime

from pydantic import BaseModel


class DocumentDetail(BaseModel):
    id: str
    title: str
    document_type: str
    source: str = ""
    summary: str = ""
    content: str
    department: str = ""
    version: str = ""
    status: str = "ACTIVE"
    effective_date: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
