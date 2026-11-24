"""Module with the DataImporter class."""

import re
from collections.abc import Callable
from typing import Any

from .database import Database
from .exceptions import UnknownObjectTypeError
from .model import FastAsCodeModel

CustomResolver = Callable[[str], str]


class DataImporter:
    """Imports data from a `data` dictionary into the database."""

    def __init__(
        self, models: dict[str, type[FastAsCodeModel]], database: Database
    ) -> None:
        """Set values."""
        self._models: dict[str, type[FastAsCodeModel]] = models
        self._database = database
        self._resolvers: dict[str, CustomResolver] = {}

    def add_resolver(self, directive: str, resolver: CustomResolver) -> None:
        """Add a resolver to the resolver list."""
        self._resolvers[directive] = resolver

    def _run_resolvers_str(self, data: dict, key: str) -> None:
        """Run the str resolvers."""
        for directive, resolver in self._resolvers.items():
            match = re.match(rf'^\[{directive}:(.+)\]$', data[key])
            if match:
                data[key] = resolver(match.groups()[0])

    def _run_resolvers(self, data: dict) -> None:
        """Run the resolvers on all str fields of the data."""
        for key, value in data.items():
            if type(value) is str:
                self._run_resolvers_str(data, key)
            elif type(value) is dict:
                self._run_resolvers(value)

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

            self._run_resolvers(obj_data)

            obj = self._parse_object(model, obj_data)
            obj.id = obj_id
            self._database.add_object(obj_id, obj)
