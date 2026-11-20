"""Module with a YAML Repo loader."""

from pathlib import Path
from typing import override

from ruamel.yaml import YAML
from ruamel.yaml.error import MarkedYAMLError

from .exceptions import YamlLoadingError
from .repo_loader import RepoLoader


class YamlRepoLoader(RepoLoader):
    """A loader for repo's with YAML files."""

    def __init__(self, repo_path: Path) -> None:
        """Set the initial values."""
        self._path = repo_path

    def discover_files(self) -> list[Path]:
        """Find all YAML files in the working directory."""
        return [
            path
            for pattern in ('*.yaml', '*.yml')
            for path in self._path.rglob(pattern, case_sensitive=True)
            if path.is_file() and not path.name.startswith('_')
        ]

    def _preprocess_file(self, file: Path) -> str:
        """Preprocess a file."""
        contents = file.read_text()
        return contents

    def _parse_file(self, file: Path, *, parser: YAML) -> list[dict]:
        """Parse a specific file."""
        contents = self._preprocess_file(file)

        try:
            documents = list(parser.load_all(contents))
            pass
        except MarkedYAMLError as exc:
            raise YamlLoadingError(
                filename=str(file), error=exc.problem
            ) from exc
        return documents

    def _check_duplicate_keys(self, data: dict[str, list[dict]]) -> None:
        """Check if there are duplicate keys."""
        seen_in: dict[str, str] = {}
        for filename, documents in data.items():
            for document in documents:
                for key in document:
                    if key.startswith('_'):
                        continue

                    first_file = seen_in.get(key)

                    if first_file is not None:
                        raise YamlLoadingError(
                            filename,
                            f'Key "{key}" is duplicate in file '
                            f'{first_file} and {filename}.',
                        )

                    seen_in[key] = filename

    def _combine_data(self, data: dict[str, list[dict]]) -> dict[str, dict]:
        """Combine the retrieved data into one data dictionary."""
        objects: dict[str, dict] = {}
        for documents in data.values():
            for document in documents:
                objects.update(
                    (key, value)
                    for key, value in document.items()
                    if not key.startswith('_')
                )

        return objects

    @override
    def retrieve_objects(self) -> dict[str, dict]:
        """Retrieve all objects from the repo."""
        files = self.discover_files()

        yaml_parser = YAML(typ='safe')

        data: dict[str, list[dict]] = {}

        # Load all data
        for file in files:
            data[str(file.relative_to(self._path))] = self._parse_file(
                file, parser=yaml_parser
            )

        self._check_duplicate_keys(data)

        return self._combine_data(data)
