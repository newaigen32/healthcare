from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document

SAMPLE_DOCUMENTS: list[dict[str, object]] = [
    {
        "id": "sop-001",
        "title": "Prior Authorization Submission Procedure",
        "document_type": "SOP",
        "source": "UM-SOP-PA-Submit-2026.pdf",
        "summary": "Steps to submit a complete prior authorization request to a commercial payer.",
        "content": (
            "Submit prior authorization requests only after eligibility is confirmed. Include the member ID, "
            "ordering provider NPI, requested CPT/HCPCS codes, diagnosis codes, and supporting clinical notes. "
            "If the payer portal is unavailable, fax the packet and log the confirmation number in the UM tracker."
        ),
        "department": "Utilization Management",
        "version": "1.2",
        "status": "active",
        "effective_date": date(2026, 1, 15),
    },
    {
        "id": "sop-002",
        "title": "Claim Denial Handling Procedure",
        "document_type": "SOP",
        "source": "Claims-SOP-Denial-2026.pdf",
        "summary": "How to review, document, and route a denied claim for correction or appeal.",
        "content": (
            "When a claim is denied, identify the CARC/RARC codes, confirm whether the denial is medical or "
            "administrative, and notify the submitter within two business days. Do not close the case until "
            "missing documentation is received or the appeal window expires."
        ),
        "department": "Claims",
        "version": "2.0",
        "status": "active",
        "effective_date": date(2026, 2, 1),
    },
    {
        "id": "sop-003",
        "title": "Eligibility Verification Procedure",
        "document_type": "SOP",
        "source": "Access-SOP-Eligibility-2026.pdf",
        "summary": "Standard steps to verify coverage before scheduling or authorizing services.",
        "content": (
            "Verify eligibility on the date of service using the payer portal or EDI 270/271. Confirm plan name, "
            "effective dates, in-network status, and copay or deductible. If coverage is inactive, stop the "
            "authorization and notify the scheduling team."
        ),
        "department": "Patient Access",
        "version": "1.1",
        "status": "active",
        "effective_date": date(2026, 1, 8),
    },
    {
        "id": "sop-004",
        "title": "Medical Necessity Documentation Procedure",
        "document_type": "SOP",
        "source": "Clinical-SOP-MedNec-2026.pdf",
        "summary": "Required clinical documentation to support medical necessity reviews.",
        "content": (
            "Medical necessity packets must include the relevant history, physical findings, prior treatments, "
            "and the clinical rationale for the requested service. Imaging requests also need the suspected "
            "diagnosis and why a lower-intensity alternative is not appropriate."
        ),
        "department": "Clinical Review",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 3, 1),
    },
    {
        "id": "sop-005",
        "title": "Authorization Expiration Follow-up Procedure",
        "document_type": "SOP",
        "source": "UM-SOP-Auth-Expiry-2026.pdf",
        "summary": "How to monitor, extend, or close authorizations that are nearing expiration.",
        "content": (
            "Review authorizations that expire within 14 days. If the service is still planned, request an "
            "extension with updated clinicals. If the service was completed, attach the date of service and "
            "close the UM case. Expired unused authorizations should be marked unused, not denied."
        ),
        "department": "Utilization Management",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 4, 1),
    },
    {
        "id": "payer-001",
        "title": "MRI Authorization Requirements",
        "document_type": "PAYER_RULE",
        "source": "Payer-Northstar-MRI-Rules.pdf",
        "summary": "Northstar Health requires prior authorization for outpatient MRI except in listed emergencies.",
        "content": (
            "Northstar Health requires prior authorization for outpatient MRI of the brain, spine, and joints. "
            "Include conservative therapy notes for at least four weeks when requesting lumbar MRI. Emergency "
            "department MRI performed during an acute visit does not require prior authorization."
        ),
        "department": "Payer Operations",
        "version": "2026.1",
        "status": "active",
        "effective_date": date(2026, 1, 1),
    },
    {
        "id": "payer-002",
        "title": "CT Scan Authorization Requirements",
        "document_type": "PAYER_RULE",
        "source": "Payer-Summit-CT-Rules.pdf",
        "summary": "Summit Care requires authorization for non-emergent CT except when cancer staging criteria are met.",
        "content": (
            "Summit Care requires prior authorization for non-emergent outpatient CT. Cancer staging CT is "
            "exempt when an oncology diagnosis and staging intent are documented. Contrast vs non-contrast must "
            "be specified on the authorization request."
        ),
        "department": "Payer Operations",
        "version": "2026.2",
        "status": "active",
        "effective_date": date(2026, 2, 15),
    },
    {
        "id": "payer-003",
        "title": "Referral Requirements for Specialty Care",
        "document_type": "PAYER_RULE",
        "source": "Payer-Lakeside-Referral-Rules.pdf",
        "summary": "Lakeside HMO requires a PCP referral before most specialty evaluations.",
        "content": (
            "Lakeside HMO members need a primary care referral before specialty evaluation for orthopedics, "
            "cardiology, and neurology. Referrals are valid for 90 days. Claims without a matching referral "
            "number are denied as not authorized."
        ),
        "department": "Payer Operations",
        "version": "3.0",
        "status": "active",
        "effective_date": date(2026, 1, 1),
    },
    {
        "id": "payer-004",
        "title": "Payer Appeal Windows",
        "document_type": "PAYER_RULE",
        "source": "Payer-Rules-Appeals-Guide.pdf",
        "summary": "Standard commercial appeal windows and required appeal packet contents.",
        "content": (
            "Most commercial payers allow 30 to 180 days to appeal a denied claim or authorization. Confirm the "
            "payer-specific window in the contract file before submitting. Include the original denial letter, "
            "clinical notes, and a point-by-point medical necessity letter."
        ),
        "department": "Appeals",
        "version": "1.4",
        "status": "active",
        "effective_date": date(2026, 1, 20),
    },
    {
        "id": "payer-005",
        "title": "Missing Clinical Documentation Denial Rule",
        "document_type": "PAYER_RULE",
        "source": "Payer-Common-CO16-Rules.pdf",
        "summary": "How payers apply documentation denials and what to attach on resubmission.",
        "content": (
            "Payers often deny with missing documentation when the progress note, imaging report, or order is "
            "absent. Resubmit with the complete note, the signed order, and the original claim number. Do not "
            "open a new claim if the payer accepts a corrected claim."
        ),
        "department": "Claims",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 3, 10),
    },
    {
        "id": "case-001",
        "title": "Sample Case: Approved MRI Prior Authorization",
        "document_type": "PAST_CASE",
        "source": "Case-UM-8801-Approved.docx",
        "summary": "Fictional case where lumbar MRI was approved after conservative therapy notes were attached.",
        "content": (
            "Case UM-8801 (fictional) requested lumbar MRI for persistent radiculopathy. The first submission "
            "lacked physical therapy notes. After the clinic attached four weeks of conservative therapy, "
            "Northstar Health approved the MRI for 45 days."
        ),
        "department": "Utilization Management",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 5, 2),
    },
    {
        "id": "case-002",
        "title": "Sample Case: Denied Authorization for Missing Clinicals",
        "document_type": "PAST_CASE",
        "source": "Case-UM-8807-Denied.docx",
        "summary": "Fictional denial issued because the request included an order but no progress note.",
        "content": (
            "Case UM-8807 (fictional) requested CT abdomen. The packet included an order only. Summit Care "
            "denied for missing clinical documentation. The team obtained the clinic progress note and "
            "resubmitted as a reconsideration rather than a new request."
        ),
        "department": "Utilization Management",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 5, 18),
    },
    {
        "id": "case-003",
        "title": "Sample Case: Missing Prior Authorization on a Claim",
        "document_type": "PAST_CASE",
        "source": "Case-Claims-4412.docx",
        "summary": "Fictional claim denied because the outpatient procedure posted without a matching authorization.",
        "content": (
            "Case 4412 (fictional) was denied for missing prior authorization. The team obtained retrospective "
            "authorization and resubmitted with the original claim number. Future claims for that CPT now "
            "check the UM tracker before billing."
        ),
        "department": "Claims",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 6, 1),
    },
    {
        "id": "case-004",
        "title": "Sample Case: Appeal After Medical Necessity Denial",
        "document_type": "PAST_CASE",
        "source": "Case-Appeals-5520.docx",
        "summary": "Fictional appeal that overturned a medical necessity denial for physical therapy visits.",
        "content": (
            "Case AP-5520 (fictional) was denied as not medically necessary after eight PT visits. The appeal "
            "included updated functional scores and a plan for four additional visits. The payer overturned "
            "the denial and authorized the remaining visits."
        ),
        "department": "Appeals",
        "version": "1.0",
        "status": "active",
        "effective_date": date(2026, 6, 12),
    },
]


def seed_documents(session: Session) -> int:
    """Insert sample documents that are not already present. Returns inserted count."""
    existing_ids = set(session.scalars(select(Document.id)).all())
    inserted = 0
    for payload in SAMPLE_DOCUMENTS:
        document_id = str(payload["id"])
        if document_id in existing_ids:
            continue
        session.add(Document(**payload))
        inserted += 1
    if inserted:
        session.commit()
    return inserted
