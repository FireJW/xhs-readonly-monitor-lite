"""Project-specific exceptions."""


class XHSReadonlyError(Exception):
    """Base exception for read-only monitor failures."""


class CDPError(XHSReadonlyError):
    """Chrome DevTools Protocol communication failed."""


class NoFeedsError(XHSReadonlyError):
    """The page did not expose feed data in its initial state."""


class NoFeedDetailError(XHSReadonlyError):
    """The page did not expose note detail data in its initial state."""


class PageNotAccessibleError(XHSReadonlyError):
    """The requested note page is not available for read-only inspection."""
