"""Module with tests for the database."""

from typing import ClassVar

import pytest
from pydantic import BaseModel, Field

from fast_as_code import FastAsCodeModel
from fast_as_code.database import Database
from fast_as_code.exceptions import (
    DuplicateIdError,
    ObjectNotFoundError,
    UnknownObjectTypeAddedError,
    UnknownObjectTypeRequestedError,
)
from fast_as_code.model import ResolvableField


class MyModel1(FastAsCodeModel):
    """First test model."""

    name: str
    my_model2_m2n: list[str] | None = None
    my_model2_o2n: str | None = None
    my_model2_o2m: str | None = None
    my_model2_m2m: list[str] | None = None

    # Resolved objects
    my_model2_m2n_objects: list[MyModel2] = Field(
        default_factory=list, exclude=True
    )
    my_model2_o2n_object: MyModel2 | None = None
    my_model2_o2m_object: MyModel2 | None = None
    my_model2_m2m_objects: list[MyModel2] = Field(
        default_factory=list, exclude=True
    )

    # Metadata
    resolvable_fields: ClassVar[list[ResolvableField]] = [
        ResolvableField(
            'my_model2_m2n', 'my_model2_m2n_objects', 'many-to-none'
        ),
        ResolvableField('my_model2_o2n', 'my_model2_o2n_object', 'one-to-none'),
        ResolvableField(
            'my_model2_o2m',
            'my_model2_o2m_object',
            'one-to-many',
            'my_model1_o2m_objs_backlink',
        ),
        ResolvableField(
            'my_model2_m2m',
            'my_model2_m2m_objects',
            'many-to-many',
            'my_model1_m2m_objs_backlink',
        ),
    ]


class MyModel2(FastAsCodeModel):
    """Second test model."""

    title: str

    # Backlinks
    my_model1_o2m_objs_backlink: list[MyModel1] = []
    my_model1_m2m_objs_backlink: list[MyModel1] = []
    my_model3_objs_backlinks: list[MyModel3] = []


class SubModel(BaseModel):
    """A submodel to test with."""

    title: str
    my_model_2: str | None = None

    # Resolved objects
    my_model_2_obj: MyModel2 | None = None

    resolvable_fields: ClassVar[list[ResolvableField]] = [
        ResolvableField(
            'my_model_2',
            'my_model_2_obj',
            'one-to-many',
            'my_model3_objs_backlinks',
        )
    ]


class MyModel3(FastAsCodeModel):
    """Third test model."""

    title: str
    submodel: SubModel

    resolvable_children: list[str] = ['submodel']


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


def test_adding_invalid_object(database: Database) -> None:
    """Test adding a object that has no type in the database."""
    obj_3_1 = MyModel3(
        title='non-existing-type', submodel=SubModel(title='test')
    )
    with pytest.raises(UnknownObjectTypeAddedError):
        database.add_object('my_model_3.test', obj_3_1)


def test_retrieving_non_exising_type(database: Database) -> None:
    """Test if we get an error on requesting unkown types."""
    with pytest.raises(UnknownObjectTypeRequestedError):
        database.get_one('my_model_3.test')


def test_retrieving_non_exising_object(database: Database) -> None:
    """Test if we get an error when requesting data that doesn't exist."""
    with pytest.raises(ObjectNotFoundError):
        database.get_one('mymodel_1.non_existing')


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


def test_resolving_objects_one_to_many(database: Database) -> None:
    """Test if we can resolve objects (one-to-many)."""
    obj_1_1 = MyModel1(
        name='Testname 1',
        my_model2_o2m='mymodel_2.obj_2_1',
    )
    obj_1_2 = MyModel1(
        name='Testname 2',
        my_model2_o2m='mymodel_2.obj_2_1',
    )
    obj_2_1 = MyModel2(title='Testname 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    database.add_object('mymodel_1.obj_1_2', obj_1_2)
    database.add_object('mymodel_2.obj_2_1', obj_2_1)

    database.resolve_all()

    assert obj_1_1.my_model2_o2m_object is not None
    assert obj_1_1.my_model2_o2m_object is obj_2_1
    assert obj_1_2.my_model2_o2m_object is not None
    assert obj_1_2.my_model2_o2m_object is obj_2_1
    assert len(obj_2_1.my_model1_o2m_objs_backlink) == 2
    assert obj_1_1 in obj_2_1.my_model1_o2m_objs_backlink
    assert obj_1_2 in obj_2_1.my_model1_o2m_objs_backlink


def test_resolving_objects_many_to_many(database: Database) -> None:
    """Test if we can resolve objects (one-to-many)."""
    obj_1_1 = MyModel1(
        name='Testname 1',
        my_model2_m2m=['mymodel_2.obj_2_1', 'mymodel_2.obj_2_2'],
    )
    obj_1_2 = MyModel1(
        name='Testname 2',
        my_model2_m2m=['mymodel_2.obj_2_2'],
    )
    obj_2_1 = MyModel2(title='Testname 2')
    obj_2_2 = MyModel2(title='Testname 2')

    database.add_object('mymodel_1.obj_1_1', obj_1_1)
    database.add_object('mymodel_1.obj_1_2', obj_1_2)
    database.add_object('mymodel_2.obj_2_1', obj_2_1)
    database.add_object('mymodel_2.obj_2_2', obj_2_2)

    database.resolve_all()

    assert len(obj_1_1.my_model2_m2m_objects) == 2
    assert len(obj_1_2.my_model2_m2m_objects) == 1
    assert obj_2_1 in obj_1_1.my_model2_m2m_objects
    assert obj_2_2 in obj_1_1.my_model2_m2m_objects
    assert obj_2_2 in obj_1_2.my_model2_m2m_objects

    assert len(obj_2_1.my_model1_m2m_objs_backlink) == 1
    assert len(obj_2_2.my_model1_m2m_objs_backlink) == 2
    assert obj_1_1 in obj_2_1.my_model1_m2m_objs_backlink
    assert obj_1_1 in obj_2_2.my_model1_m2m_objs_backlink
    assert obj_1_2 in obj_2_2.my_model1_m2m_objs_backlink


def test_resolving_child_objects() -> None:
    """Test if we can resolve fields in child objects."""
    database = Database(
        models={
            'mymodel_1': MyModel1,
            'mymodel_2': MyModel2,
            'mymodel_3': MyModel3,
        }
    )

    obj_2_1 = MyModel2(title='Testname 2')
    obj_3_1 = MyModel3(
        title='test',
        submodel=SubModel(title='test', my_model_2='mymodel_2.obj_2_1'),
    )

    database.add_object('mymodel_2.obj_2_1', obj_2_1)
    database.add_object('mymodel_3.obj_3_1', obj_3_1)

    database.resolve_all()

    assert obj_3_1.submodel.my_model_2_obj is not None
    assert obj_3_1.submodel.my_model_2_obj is obj_2_1
    assert len(obj_2_1.my_model3_objs_backlinks) == 1
    assert obj_3_1 in obj_2_1.my_model3_objs_backlinks
