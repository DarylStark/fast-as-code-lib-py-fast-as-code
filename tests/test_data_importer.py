"""Tests for the DataImporter class."""

from pathlib import Path

import pytest
from models import MyModel1, MyModel2, MyModel3

from fast_as_code import Database, DataImporter, FastAsCodeModel
from fast_as_code.exceptions import (
    UnknownObjectTypeError,
)
from fast_as_code.resolvers import FileResolver


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


def test_importing_with_custom_resolver(
    database: Database, data_importer: DataImporter
) -> None:
    """Test if we can import data."""

    def reverse_str(s: str) -> str:
        """Test resolver to reverse a str."""
        return s[::-1]

    data_importer.add_resolver('rev', reverse_str)
    data_importer.import_data({'mymodel_1.test_1': {'name': '[rev:lyrad]'}})

    assert len(database.get_all(MyModel1)) == 1
    assert database.get_all(MyModel1)['mymodel_1.test_1'].name == 'daryl'


def test_importing_with_fileresolver(
    model_list: dict[str, type[FastAsCodeModel]], yaml_repo_folder: Path
) -> None:
    """Test if we can resolve a file."""
    model_list['mymodel_3'] = MyModel3
    database = Database(models=model_list)
    data_importer = DataImporter(model_list, database)

    file_resolver = FileResolver(root_path=yaml_repo_folder)

    data_importer.add_resolver('file', file_resolver)
    data_importer.import_data(
        {
            'mymodel_3.test_1': {
                'title': '[file:text_files/my_test_file.txt]',
                'city': 'Zaandam',
                'age': 40,
                'submodel': {'title': '[file:text_files/my_test_file.txt]'},
            }
        }
    )

    obj = database.get_all(MyModel3)['mymodel_3.test_1']

    assert obj.title == 'this is my test-file'
    assert obj.submodel.title == 'this is my test-file'
