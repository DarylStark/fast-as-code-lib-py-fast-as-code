"""Test custom resolvers."""

from pathlib import Path

from fast_as_code.resolvers import FileResolver


def test_resolving_files(yaml_repo_folder: Path) -> None:
    """Test the `FileResolver` class."""
    fr = FileResolver(yaml_repo_folder / 'text_files')
    cnt = fr('my_test_file.txt')
    assert cnt == 'this is my test-file'
