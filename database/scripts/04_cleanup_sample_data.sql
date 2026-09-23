-- Removes only the synthetic development records from 02_insert_sample_data.sql.
-- Does not drop the documents table or the database.
-- Do not run this during normal application startup.

DELETE FROM documents
WHERE id IN (
    'sop-001',
    'sop-002',
    'sop-003',
    'sop-004',
    'sop-005',
    'payer-001',
    'payer-002',
    'payer-003',
    'payer-004',
    'payer-005',
    'case-001',
    'case-002',
    'case-003',
    'case-004',
    'case-005'
);
