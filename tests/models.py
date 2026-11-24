"""Models to test with."""

from typing import ClassVar

from pydantic import BaseModel, Field

from fast_as_code import FastAsCodeModel
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
    city: str | None = None
    age: int = 0
    submodel: SubModel

    resolvable_children: list[str] = ['submodel']
