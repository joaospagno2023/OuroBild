from pathlib import Path

from app.models.project.project import Project
from app.repositories.json_project_repository import JsonProjectRepository


def test_get_all_returns_project_list():
    """
    Deve retornar uma lista de objetos Project.
    """

    repository = JsonProjectRepository(
        Path("config")
    )

    projects = repository.get_all()

    assert isinstance(projects, list)

    if projects:
        assert isinstance(projects[0], Project)