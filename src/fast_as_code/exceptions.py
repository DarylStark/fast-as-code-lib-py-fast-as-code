"""Module with exceptions for the library."""


class FastAsCodeError(BaseException):
    """Base class for all Fast-As-Code Errors."""


class DoubleModelNameError(FastAsCodeError):
    """Error when a user tries to register a already existing model."""

    def __init__(self, model_name: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(f'Model name already registered: "{model_name}".')


class DatabaseNotInitializedError(FastAsCodeError):
    """Error when the database is not intialized."""


class AlreadyInitializedError(FastAsCodeError):
    """Error when trying to initialize a already initialized app."""


class DatabaseError(FastAsCodeError):
    """Base class for errors with the database."""


class DuplicateIdError(DatabaseError):
    """Error for duplicate keys."""

    def __init__(self, obj_id: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(
            f'Object with id "{obj_id}" is already in the database'
        )


class UnknownObjectTypeAddedError(DatabaseError):
    """Error for when a unknown obj-type is being added to the database."""

    def __init__(self, obj_id: str, obj_type: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(
            f'Unknown object added to database: "{obj_type}" '
            f'for resource "{obj_id}".'
        )


class UnknownObjectTypeRequestedError(DatabaseError):
    """Error for when a unknown obj-id is being requested from the database."""

    def __init__(self, obj_id: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(
            f'Unknown object type requested from the database: "{obj_id}".'
        )


class ObjectNotFoundError(DatabaseError):
    """Error for when a unknown obj-id is being requested from the database."""

    def __init__(self, obj_id: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(
            f'Unknown object requested from the database: "{obj_id}".'
        )


class YamlRepoLoaderError(FastAsCodeError):
    """Base class for all YamlRepoLoader errors."""


class YamlLoadingError(YamlRepoLoaderError):
    """Errors that occur while loading a Yaml file."""

    def __init__(self, filename: str, error: str) -> None:
        """Call the baseclass with the correct message."""
        super().__init__(f'{filename}: {error}')
