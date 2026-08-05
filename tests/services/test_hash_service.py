from pathlib import Path

from app.services.hash_service import (
    HashService,
)


def test_calculate_file_hash(tmp_path):
    """
    Deve calcular corretamente o SHA256
    de um arquivo.
    """

    #
    # Arrange
    #

    file = tmp_path / "arquivo.txt"

    file.write_text(
        "OuroBuild",
        encoding="utf-8",
    )

    service = HashService()

    #
    # Act
    #

    hash_value = service.calculate_file_hash(
        file,
    )

    #
    # Assert
    #

    assert hash_value != ""

    assert len(hash_value) == 64