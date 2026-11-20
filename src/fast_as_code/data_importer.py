"""Module with the DataImporter class."""

from typing import Any

from .database import Database
from .exceptions import UnknownObjectTypeError
from .model import FastAsCodeModel


class DataImporter:
    """Imports data from a `data` dictionary into the database."""

    def __init__(
        self, models: dict[str, type[FastAsCodeModel]], database: Database
    ) -> None:
        """Set values."""
        self._models: dict[str, type[FastAsCodeModel]] = models
        self._database = database

    def _parse_object[ResourceModel: FastAsCodeModel](
        self,
        model: type[ResourceModel],
        obj: dict[str, Any],
    ) -> ResourceModel:
        """Generic method to parse data."""
        return model.model_validate(obj, extra='forbid')

    def import_data(self, data: dict[str, dict]) -> None:
        """Import data from a dict into the database."""
        for obj_id, obj_data in data.items():
            obj_type = obj_id.split('.', maxsplit=1)[0]
            model = self._models.get(obj_type)
            if not model:
                raise UnknownObjectTypeError(obj_id, obj_type)

            obj = self._parse_object(model, obj_data)
            obj.id = obj_id
            self._database.add_object(obj_id, obj)
