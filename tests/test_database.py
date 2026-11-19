"""Module with tests for the database."""

from typing import ClassVar

import pytest
from pydantic import Field

from fast_as_code import FastAsCodeModel
from fast_as_code.database import Database
from fast_as_code.exceptions import DuplicateIdError
from fast_as_code.model import ResolvableField


class MyModel1(FastAsCodeModel):
    """First test model."""

    name: str
    my_model2_m2n: list[str] | None = None
    my_model2_o2n: str | None = None

    # Resolved objects
    my_model2_m2n_objects: list[MyModel2] = Field(
        default_factory=list, exclude=True
    )
    my_model2_o2n_object: MyModel2 | None = None

    # Metadata
    resolvable_fields: ClassVar[list[ResolvableField]] = [
        ResolvableField(
            'my_model2_m2n', 'my_model2_m2n_objects', 'many-to-none'
        ),
        ResolvableField('my_model2_o2n', 'my_model2_o2n_object', 'one-to-none'),
    ]


class MyModel2(FastAsCodeModel):
    """Second test model."""

    title: str


@pytest.fixture(scope='function')
def database() -> Database:
    """Database to test with."""
    return Database(
        models={
            'mymodel_1': MyModel1,
            'mymodel_2': MyModel2,
        }
    )


def test_initializing_database(
    database: Database,
) -> None:
    """Test initializing the database class with a dummy model."""
    assert len(database.get_models()) == 2
    assert MyModel1 in database.get_models()
    assert MyModel2 in database.get_models()


def test_adding_and_retrieving_data(
    database: Database,
) -> None:
    """Test adding and retrieving data."""
    obj_1_1 = MyModel1(name='Testname 1')
    obj_1_2 = MyModel1(name='Testname 2')
    obj_2_1 = MyModel2(title='Testtitle 1')
    obj_2_2 = MyModel2(title='Testtitle 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    database.add_object('mymodel_1.obj_1_2', obj_1_2)
    database.add_object('mymodel_2.obj_2_1', obj_2_1)
    database.add_object('mymodel_2.obj_2_2', obj_2_2)

    assert database.get_one('mymodel_1.obj_1_1') is not None
    assert database.get_one('mymodel_1.obj_1_2') is not None
    assert database.get_one('mymodel_2.obj_2_1') is not None
    assert database.get_one('mymodel_2.obj_2_2') is not None

    assert len(database.get_all(MyModel1)) == 2
    assert len(database.get_all(MyModel2)) == 2

    assert len(database.get_all_values(MyModel1)) == 2
    assert len(database.get_all_values(MyModel2)) == 2

    assert len(database.get_all_values_for_all_types()) == 4


def test_error_on_adding_duplicates(database: Database) -> None:
    """Test if we get errors on adding duplicate ids."""
    obj_1_1 = MyModel1(name='Testname 1')
    obj_1_2 = MyModel1(name='Testname 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    with pytest.raises(DuplicateIdError):
        database.add_object('mymodel_1.obj_1_1', obj_1_2)


def test_resolving_objects_many_to_none(database: Database) -> None:
    """Test if we can resolve objects (many-to-none)."""
    obj_1_1 = MyModel1(
        name='Testname 1',
        my_model2_m2n=['mymodel_2.obj_2_1', 'mymodel_2.obj_2_2'],
    )
    obj_2_1 = MyModel2(title='Testname 2')
    obj_2_2 = MyModel2(title='Testname 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    database.add_object('mymodel_2.obj_2_1', obj_2_1)
    database.add_object('mymodel_2.obj_2_2', obj_2_2)

    database.resolve_all()

    assert len(obj_1_1.my_model2_m2n_objects) == 2
    assert obj_2_1 in obj_1_1.my_model2_m2n_objects
    assert obj_2_2 in obj_1_1.my_model2_m2n_objects


def test_resolving_objects_one_to_none(database: Database) -> None:
    """Test if we can resolve objects (one-to-none)."""
    obj_1_1 = MyModel1(
        name='Testname 1',
        my_model2_o2n='mymodel_2.obj_2_1',
    )
    obj_2_1 = MyModel2(title='Testname 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    database.add_object('mymodel_2.obj_2_1', obj_2_1)

    database.resolve_all()

    assert obj_1_1.my_model2_o2n_object is not None
    assert obj_1_1.my_model2_o2n_object is obj_2_1
