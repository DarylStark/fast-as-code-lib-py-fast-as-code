"""Tests for the DataImporter class."""

import pytest
from models import MyModel1, MyModel2

from fast_as_code import Database, DataImporter
from fast_as_code.exceptions import (
    UnknownObjectTypeError,
)


def test_importing_data(
    database: Database, data_importer: DataImporter
) -> None:
    """Test if we can import data."""
    data_importer.import_data({'mymodel_1.test_1': {'name': 'test_model_1_1'}})
    data_importer.import_data({'mymodel_1.test_2': {'name': 'test_model_1_2'}})
    data_importer.import_data({'mymodel_2.test_1': {'title': 'test_model_1_1'}})
    data_importer.import_data({'mymodel_2.test_2': {'title': 'test_model_1_2'}})

    assert len(database.get_all(MyModel1)) == 2
    assert len(database.get_all(MyModel2)) == 2


def test_importing_unknown_type(data_importer: DataImporter) -> None:
    """Test if we can import data."""
    with pytest.raises(UnknownObjectTypeError):
        data_importer.import_data(
            {'mymodel_3.test_1': {'title': 'test_model_1_1'}}
        )
