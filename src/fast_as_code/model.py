"""Module with the models for the application."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

relac_models: dict[str, type[FastAsCodeModel]] = {}


@dataclass
class ResolvableField:
    """Field that can be resolved."""

    source_field: str
    destination_field: str
    type: Literal['many-to-many', 'one-to-many', 'one-to-none', 'many-to-none']
    populates_back: str | None = None


@dataclass
class LintingFinding:
    """Class for a Linting Error."""

    id: str
    resource_id: str | None
    error: str


class FastAsCodeModel(BaseModel):
    """Base model for resources."""

    id: str | None = Field(default=None, exclude=False)
    resource_linting_ignores: list[str] | None = None

    def get_linting_findings(
        self, use_ignores: bool = True
    ) -> list[LintingFinding]:
        """Get linting findings."""
        findings = self.linting_findings
        ignores = self.resource_linting_ignores or []
        return [
            finding
            for finding in findings
            if finding.id not in ignores or not use_ignores
        ]

    @property
    def linting_findings(self) -> list[LintingFinding]:
        """Get linting findings for the model."""
        return []

    def __repr__(self) -> str:
        """The repr for this model."""
        return str(self)

    def __str__(self) -> str:
        """The str representation for this model."""
        return f'<{type(self).__name__}: "{self.id}">'
