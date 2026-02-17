class ApplicationError(Exception):
    pass


class ValidationError(ApplicationError):
    pass


class NotFoundError(ApplicationError):
    pass
