"""Module with the FastAsCode class."""

from collections.abc import Callable

from .database import Database
from .exceptions import (
    AlreadyInitializedError,
    DatabaseNotInitializedError,
    DoubleModelNameError,
)
from .model import FastAsCodeModel


class FastAsCode:
    """FastAsCode application facade class."""

    def __init__(self) -> None:
        """Configure the application."""
        self._database: Database | None = None
        self._models: dict[str, type[FastAsCodeModel]] = {}

    def register_model[TResource: FastAsCodeModel](
        self,
        model_name: str,
    ) -> Callable[[type[TResource]], type[TResource]]:
        """Decorator to register a model for data."""

        def model_decorator(class_: type[TResource]) -> type[TResource]:
            if model_name in self._models:
                raise DoubleModelNameError(model_name)
            self._models[model_name] = class_
            return class_

        return model_decorator

    def get_models(self) -> dict[str, type[FastAsCodeModel]]:
        """Get all models in the database."""
        return self._models

    def initialize(self) -> None:
        """Initialize the application."""
        if self._database:
            raise AlreadyInitializedError('Application is already initialized')
        self._database = Database(self._models)

    @property
    def database(self) -> Database:
        """Retrieve the database for the application."""
        if self._database is None:
            raise DatabaseNotInitializedError('Databae is not initialized')
        return self._database
