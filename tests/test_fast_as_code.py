"""Tests for FastAsCode."""

import pytest

from fast_as_code import FastAsCode, FastAsCodeModel
from fast_as_code.exceptions import (
    AlreadyInitializedError,
    DatabaseNotInitializedError,
    DoubleModelNameError,
)


def test_empty_object() -> None:
    """Test if we get an empty list of models on initialization."""
    app = FastAsCode()
    assert len(app.get_models()) == 0


def test_registering_models() -> None:
    """Test if we can register models."""
    app = FastAsCode()

    @app.register_model('mymodel1')
    class MyModel1(FastAsCodeModel):
        """First test model."""

        name: str

    @app.register_model('mymodel2')
    class MyModel2(FastAsCodeModel):
        """Second test model."""

        title: str

    assert len(app.get_models()) == 2
    assert 'mymodel1' in app.get_models()
    assert 'mymodel2' in app.get_models()


def test_registering_model_name_twice() -> None:
    """Test if we get an error when registering the same modelname twice."""
    app = FastAsCode()

    @app.register_model('mymodel1')
    class MyModel1(FastAsCodeModel):
        """First test model."""

        name: str

    with pytest.raises(DoubleModelNameError):

        @app.register_model('mymodel1')
        class MyModel2(FastAsCodeModel):
            """Second test model."""

            title: str


def test_error_on_non_initialized_db() -> None:
    """Test if we get an error when retrieving a non-initialized db."""
    app = FastAsCode()
    with pytest.raises(DatabaseNotInitializedError):
        _ = app.database


def test_retrieving_db() -> None:
    """Test if we can retrieve the database after initializing."""
    app = FastAsCode()
    app.initialize()
    db = app.database
    assert db is not None


def test_initialize_twice() -> None:
    """Test if we get an error when initializing twice."""
    app = FastAsCode()
    app.initialize()
    with pytest.raises(AlreadyInitializedError):
        app.initialize()
