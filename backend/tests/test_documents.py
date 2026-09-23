import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.routes.documents import get_document


def test_get_document_by_id_succeeds(session: Session) -> None:
    detail = get_document("sop-001", session)
    assert detail.id == "sop-001"
    assert detail.document_type == "SOP"
    assert "Prior Authorization" in detail.title


def test_get_unknown_document_returns_404(session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_document("does-not-exist", session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Document not found."
