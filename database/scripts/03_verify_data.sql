SELECT COUNT(*) AS document_count
FROM documents;

SELECT
    id,
    title,
    document_type,
    status
FROM documents
ORDER BY document_type, id;

SELECT
    id,
    title,
    document_type
FROM documents
WHERE id ILIKE '%authorization%'
   OR title ILIKE '%authorization%'
   OR summary ILIKE '%authorization%'
   OR content ILIKE '%authorization%'
ORDER BY id;

SELECT
    id,
    title,
    document_type
FROM documents
WHERE id ILIKE '%sop-001%'
   OR title ILIKE '%sop-001%'
   OR summary ILIKE '%sop-001%'
   OR content ILIKE '%sop-001%'
ORDER BY id;

SELECT id, title
FROM documents
WHERE document_type = 'SOP'
ORDER BY id;

SELECT COUNT(*) AS sop_count
FROM documents
WHERE document_type = 'SOP';

SELECT id, title, summary
FROM documents
WHERE title ILIKE '%authorization%'
   OR summary ILIKE '%authorization%'
   OR content ILIKE '%authorization%'
ORDER BY id;
