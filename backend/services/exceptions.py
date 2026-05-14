class ContentBlockedException(Exception):
    """Raised when content is blocked by the ContentFilter."""
    def __init__(self, message="Content blocked.", category=None):
        super().__init__(message)
        self.category = category

class NotFoundException(Exception):
    """Raised when a requested resource is not found."""
    pass
