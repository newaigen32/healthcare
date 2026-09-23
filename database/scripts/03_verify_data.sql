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
WHERE title ILIKE '%authorization%'
   OR summary ILIKE '%authorization%'
   OR content ILIKE '%authorization%'
ORDER BY id;
