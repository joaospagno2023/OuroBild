"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project_metadata_repository_integration.py
Descrição : Teste de integração da metadata do projeto.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.repositories.json_project_metadata_repository import (
    JsonProjectMetadataRepository,
)
from app.services.hash_service import (
    HashService,
)
from app.services.project_metadata_service import (
    ProjectMetadataService,
)


def test_should_create_metadata_file(tmp_path):
    """
    Deve criar e carregar a metadata do projeto.
    """

    #
    # Arrange
    #

    metadata_path = tmp_path / "metadata"

    repository = JsonProjectMetadataRepository(
        metadata_path=metadata_path,
    )

    service = ProjectMetadataService(
        repository=repository,
        hash_service=HashService(),
    )

    project_file = tmp_path / "Projeto.csproj"

    project_file.write_text(
        "<Project />",
        encoding="utf-8",
    )

    #
    # Act
    #

    created = service.update_from_analysis(
        project_id="ProjetoTeste",
        project_file=project_file,
    )

    loaded = repository.load(
        "ProjetoTeste",
    )

    #
    # Assert
    #

    assert loaded is not None

    assert loaded.project_id == created.project_id

    assert loaded.project_hash == created.project_hash

    assert loaded.analysis_version == "1.0"

    assert (
        metadata_path
        / "ProjetoTeste"
        / "metadata.json"
    ).exists()