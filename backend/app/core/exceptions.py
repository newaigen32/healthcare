from fastapi import HTTPException, status


class SearchServiceError(Exception):
    """Raised when search cannot be completed."""


class SearchConfigurationError(SearchServiceError):
    """Raised when Azure Search is misconfigured."""


class SearchAuthenticationError(SearchServiceError):
    """Raised when Azure Search rejects credentials."""


class SearchTimeoutError(SearchServiceError):
    """Raised when Azure Search times out."""


class SearchUpstreamError(SearchServiceError):
    """Raised when Azure Search returns an unexpected response."""


def http_error_from_search_exception(exc: SearchServiceError) -> HTTPException:
    if isinstance(exc, SearchAuthenticationError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Search authentication failed. Please contact an administrator.",
        )
    if isinstance(exc, SearchTimeoutError):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The search service timed out. Please try again.",
        )
    if isinstance(exc, SearchConfigurationError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search is not configured. Please contact an administrator.",
        )
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="We couldn't complete the search. Please try again.",
    )
