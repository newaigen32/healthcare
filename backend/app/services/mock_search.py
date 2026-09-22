from app.services.static_search import StaticSearchProvider


class MockSearchProvider(StaticSearchProvider):
    """Local static catalog used when SEARCH_PROVIDER=mock."""
