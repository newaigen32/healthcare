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
    'case-005',
    'sop-006',
    'sop-007',
    'sop-008',
    'sop-009',
    'sop-010',
    'sop-011',
    'sop-012',
    'sop-013',
    'sop-014',
    'sop-015',
    'sop-016',
    'sop-017',
    'sop-018',
    'sop-019',
    'sop-020',
    'sop-021',
    'sop-022',
    'sop-023'
);
