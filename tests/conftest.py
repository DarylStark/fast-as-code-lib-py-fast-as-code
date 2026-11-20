"""Test configuration for PyTest."""

import pytest
from models import MyModel1, MyModel2

from fast_as_code import DataImporter, FastAsCodeModel
from fast_as_code.database import Database


@pytest.fixture(scope='function')
def model_list() -> dict[str, type[FastAsCodeModel]]:
    """Models to test with."""
    return {
        'mymodel_1': MyModel1,
        'mymodel_2': MyModel2,
    }


@pytest.fixture(scope='function')
def database(model_list: dict[str, type[FastAsCodeModel]]) -> Database:
    """Database to test with."""
    return Database(models=model_list)


@pytest.fixture(scope='function')
def data_importer(
    model_list: dict[str, type[FastAsCodeModel]], database: Database
) -> DataImporter:
    """DataImporter to test with."""
    return DataImporter(model_list, database)
