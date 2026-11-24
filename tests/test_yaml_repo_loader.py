"""Tests for the YamlRepoLoader class."""

from pathlib import Path

import pytest

from fast_as_code import YamlRepoLoader
from fast_as_code.exceptions import YamlLoadingError


def test_importing_data_trivial_dir(yaml_repo_folder: Path) -> None:
    """Test if we can import data."""
    loader = YamlRepoLoader(repo_path=yaml_repo_folder / 'trivial')
    data = loader.retrieve_objects()
    assert len(data) == 3
    assert 'mymodel_1.my_obj_1_1' in data
    assert 'mymodel_1.my_obj_1_2' in data
    assert 'mymodel_1.my_obj_1_3' in data
    assert '_my_skipped_model.skipped' not in data


def test_importing_data_duplicate_key(yaml_repo_folder: Path) -> None:
    """Test if we get an error on data with a duplicate key."""
    loader = YamlRepoLoader(repo_path=yaml_repo_folder / 'duplicate_key')
    with pytest.raises(YamlLoadingError):
        loader.retrieve_objects()


def test_importing_data_with_a_invalid_repo(yaml_repo_folder: Path) -> None:
    """Test if we can import data referencing a file."""
    loader = YamlRepoLoader(repo_path=yaml_repo_folder / 'invalid_yaml')
    with pytest.raises(YamlLoadingError):
        loader.retrieve_objects()
