from pathlib import Path

from app.models.project.project_metadata import (
    ProjectMetadata,
)
from app.services.hash_service import (
    HashService,
)
from app.services.project_metadata_service import (
    ProjectMetadataService,
)


class FakeRepository:

    def __init__(self):
        self.metadata = None

    def load(self, project_id):
        return self.metadata

    def save(self, metadata):
        self.metadata = metadata

    def exists(self, project_id):
        return self.metadata is not None

    def delete(self, project_id):
        self.metadata = None


def test_update_from_analysis(tmp_path):

    #
    # Arrange
    #

    project_file = tmp_path / "Projeto.csproj"

    project_file.write_text(
        "<Project />",
        encoding="utf-8",
    )

    repository = FakeRepository()

    service = ProjectMetadataService(
        repository=repository,
        hash_service=HashService(),
    )

    #
    # Act
    #

    metadata = service.update_from_analysis(
        project_id="Projeto",
        project_file=project_file,
    )

    #
    # Assert
    #

    assert isinstance(
        metadata,
        ProjectMetadata,
    )

    assert metadata.project_id == "Projeto"

    assert metadata.project_hash != ""

    assert len(metadata.project_hash) == 64

    assert repository.metadata is not None