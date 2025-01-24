class MissingConfigError(Exception):
    """The attempted operation requires configuration which is not available"""


class NeedConfirmation(Exception):
    """The user must explicitly confirm that they want to proceed"""


class NotFoundError(ValueError):
    """The requested resource was not found in the system"""
