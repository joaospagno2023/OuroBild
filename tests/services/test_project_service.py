"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project_service.py
Descrição : Testes do serviço de projetos.
--------------------------------------------------------------------
"""

from unittest.mock import Mock

import pytest

from app.models.build.compilation_engine import CompilationEngine
from app.models.build.compilation_target import CompilationTarget
from app.models.project.create_project_request import CreateProjectRequest
from app.models.project.project import Project
from app.models.project.project_type import ProjectType
from app.models.project.update_project_request import UpdateProjectRequest
from app.services.project_service import ProjectService


@pytest.fixture
def project() -> Project:
    return Project(
        id="projeto-teste",
        name="Projeto Teste",
        description="Descrição do projeto teste",
        type=ProjectType.CLIENT,
        solution_path=None,
        project_path=r"c:\projeto\teste.csproj",
        compilation_target=CompilationTarget.SOLUTION,
        compilation_engine=CompilationEngine.MSBUILD,
        publish_path=r"bin\Release",
        publish_profile=None,
        aip_path="Projeto.aip",
        visualstudio_setup_path=None,
        output_msi="Projeto.msi",
        network_path=r"\\Servidor\Builds",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


@pytest.fixture
def create_request() -> CreateProjectRequest:
    return CreateProjectRequest(
        id="projeto-teste",
        name="Projeto Teste",
        description="Descrição do projeto teste",
        type=ProjectType.CLIENT,
        project_path=r"c:\projeto\teste.csproj",
        compilation_target=CompilationTarget.SOLUTION,
        compilation_engine=CompilationEngine.MSBUILD,
        publish_path=r"bin\Release",
        aip_path="Projeto.aip",
        output_msi="Projeto.msi",
        network_path=r"\\Servidor\Builds",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


@pytest.fixture
def update_request() -> UpdateProjectRequest:
    return UpdateProjectRequest(
        name="Projeto Teste Alterado",
        description="Descrição alterada",
        type=ProjectType.CLIENT,
        project_path=r"c:\projeto\alterado.csproj",
        compilation_target=CompilationTarget.SOLUTION,
        compilation_engine=CompilationEngine.MSBUILD,
        publish_path=r"bin\Release",
        aip_path="ProjetoAlterado.aip",
        output_msi="ProjetoAlterado.msi",
        network_path=r"\\Servidor\Builds",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def test_constructor_rejects_null_repository() -> None:
    with pytest.raises(
        ValueError,
        match="ProjectRepository não foi informado.",
    ):
        ProjectService(None)


def test_get_all_delegates_to_repository() -> None:
    repository = Mock()

    projects = [
        Mock(spec=Project),
    ]

    repository.get_all.return_value = projects

    service = ProjectService(repository)

    result = service.get_all()

    assert result == projects
    repository.get_all.assert_called_once_with()


def test_get_by_id_delegates_to_repository(
    project: Project,
) -> None:
    repository = Mock()

    repository.get_by_id.return_value = project

    service = ProjectService(repository)

    result = service.get_by_id(
        "projeto-teste",
    )

    assert result == project

    repository.get_by_id.assert_called_once_with(
        "projeto-teste",
    )


def test_create_rejects_duplicate_project(
    project: Project,
    create_request: CreateProjectRequest,
) -> None:
    repository = Mock()

    repository.get_by_id.return_value = project

    service = ProjectService(repository)

    with pytest.raises(
        ValueError,
        match="ProjectId já está cadastrado.",
    ):
        service.create(
            create_request,
        )

    repository.create.assert_not_called()


def test_create_delegates_to_repository(
    project: Project,
    create_request: CreateProjectRequest,
) -> None:
    repository = Mock()

    repository.get_by_id.return_value = None
    repository.create.return_value = project

    service = ProjectService(repository)

    result = service.create(
        create_request,
    )

    assert result == project

    repository.get_by_id.assert_called_once_with(
        "projeto-teste",
    )

    repository.create.assert_called_once()


def test_update_rejects_missing_project(
    update_request: UpdateProjectRequest,
) -> None:
    repository = Mock()

    repository.get_by_id.return_value = None

    service = ProjectService(repository)

    with pytest.raises(
        ValueError,
        match="Projeto não encontrado.",
    ):
        service.update(
            "projeto-inexistente",
            update_request,
        )

    repository.update.assert_not_called()


def test_update_delegates_to_repository(
    project: Project,
    update_request: UpdateProjectRequest,
) -> None:
    repository = Mock()

    repository.get_by_id.return_value = project
    repository.update.return_value = project

    service = ProjectService(repository)

    result = service.update(
        "projeto-teste",
        update_request,
    )

    assert result == project

    repository.get_by_id.assert_called_once_with(
        "projeto-teste",
    )

    repository.update.assert_called_once()


def test_update_status_delegates_to_repository() -> None:
    repository = Mock()

    project = Mock(spec=Project)

    repository.update_status.return_value = project

    service = ProjectService(repository)

    result = service.update_status(
        "projeto-teste",
        False,
    )

    assert result == project

    repository.update_status.assert_called_once_with(
        project_id="projeto-teste",
        enabled=False,
    )