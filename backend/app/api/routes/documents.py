from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.documents import DocumentDetail

router = APIRouter(prefix="/api", tags=["documents"])

DOCUMENT_SQL = """
SELECT
    id,
    title,
    document_type,
    source,
    summary,
    content,
    department,
    version,
    status,
    effective_date,
    created_at,
    updated_at
FROM documents
WHERE id = :document_id
"""


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document(document_id: str, session: Session = Depends(get_db)) -> DocumentDetail:
    row = session.execute(text(DOCUMENT_SQL), {"document_id": document_id}).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return DocumentDetail.model_validate(dict(row))
