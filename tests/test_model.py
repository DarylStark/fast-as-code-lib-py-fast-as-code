"""Tests for the model."""

from typing import override

from fast_as_code import FastAsCodeModel
from fast_as_code.model import LintingFinding


class ModelNoLinting(FastAsCodeModel):
    """Model without linting findings."""

    name: str


class MyModel1(FastAsCodeModel):
    """Test model with linting findings."""

    name: str

    @override
    @property
    def linting_findings(self) -> list[LintingFinding]:
        """Fake linting findings for this object."""
        return [
            LintingFinding(
                id='test.finding1', resource_id=self.id, error='MyError - 1'
            ),
            LintingFinding(
                id='test.finding2', resource_id=self.id, error='MyError - 2'
            ),
        ]


def test_repr_str() -> None:
    """Test the `__repr__` and `__str__` methods of the model."""
    model = MyModel1(id='mymodel_1.model', name='test')

    assert repr(model) == '<MyModel1: "mymodel_1.model">'
    assert str(model) == repr(model)


def test_linting() -> None:
    """Test if we can get all linting results."""
    model = MyModel1(
        id='mymodel_1.model',
        name='test',
        resource_linting_ignores=['test.finding1'],
    )
    lintings = model.get_linting_findings(use_ignores=False)
    assert len(lintings) == 2


def test_linting_with_ignores() -> None:
    """Test if we can get all linting results expcept the ignores`."""
    model = MyModel1(
        id='mymodel_1.model',
        name='test',
        resource_linting_ignores=['test.finding1'],
    )
    lintings = model.get_linting_findings(use_ignores=True)
    assert len(lintings) == 1


def test_linting_not_defined() -> None:
    """Test if we get nothing when no linting is defined."""
    model = ModelNoLinting(name='test')
    assert len(model.linting_findings) == 0
