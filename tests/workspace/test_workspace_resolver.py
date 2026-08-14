"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_workspace_resolver.py
Descrição : Testes do WorkspaceResolver.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.models.environment.build_environment import (
    BuildEnvironment,
)

from app.models.project.project import (
    Project,
)

from app.workspace.workspace_context import (
    WorkspaceContext,
)

from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)


def create_project() -> Project:
    """
    Cria um projeto mínimo para os testes.
    """

    return Project(
        id="linkpagamento",
        name="LinkPagamento",
        description="Serviço LinkPagamento",
        type="client",
        solution_path=None,
        project_path=(
            r"02-Source\01-Client"
            r"\LinkPagamento"
            r"\LinkPagamento.csproj"
        ),
        compilation_target="project",
        compilation_engine="msbuild",
        publish_path=(
            r"bin\Release\publish"
        ),
        aip_path=(
            r"Setup\LinkPagamento.aip"
        ),
        output_msi="LinkPagamento.msi",
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_environment() -> BuildEnvironment:
    """
    Cria um ambiente mínimo para os testes.
    """

    return BuildEnvironment(
        id="producao",
        name="Produção",
        resolver="static",
        root_path=Path(
            r"C:\DvpLocal\WorkSpaceTFS"
            r"\OuroNet\Scc\Producao\OuroNet"
        ),
    )


def create_resolver(
    project_repository=None,
    environment_repository=None,
) -> WorkspaceResolver:
    """
    Cria um WorkspaceResolver com suas dependências.
    """

    if project_repository is None:
        project_repository = MagicMock(
            spec=ProjectRepository,
        )

    if environment_repository is None:
        environment_repository = MagicMock(
            spec=EnvironmentRepository,
        )

    return WorkspaceResolver(
        project_repository=(
            project_repository
        ),
        environment_repository=(
            environment_repository
        ),
    )


def test_deve_resolver_workspace_com_projeto_e_ambiente():
    """
    Deve resolver corretamente um projeto dentro
    de um ambiente.
    """

    project = create_project()

    environment = create_environment()

    project_repository = MagicMock(
        spec=ProjectRepository,
    )

    environment_repository = MagicMock(
        spec=EnvironmentRepository,
    )

    project_repository.get_by_id.return_value = (
        project
    )

    environment_repository.get_by_id.return_value = (
        environment
    )

    resolver = create_resolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    result = resolver.resolve(
        project_id="linkpagamento",
        environment_id="producao",
    )

    assert isinstance(
        result,
        WorkspaceContext,
    )

    assert result.project is project

    assert result.environment is environment

    assert result.project_file == (
        environment.root_path
        / project.project_path
    )


def test_deve_buscar_projeto_pelo_project_id():
    """
    Deve utilizar o project_id informado para
    buscar o projeto no repositório.
    """

    project = create_project()

    environment = create_environment()

    project_repository = MagicMock(
        spec=ProjectRepository,
    )

    environment_repository = MagicMock(
        spec=EnvironmentRepository,
    )

    project_repository.get_by_id.return_value = (
        project
    )

    environment_repository.get_by_id.return_value = (
        environment
    )

    resolver = create_resolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    resolver.resolve(
        project_id="linkpagamento",
        environment_id="producao",
    )

    project_repository.get_by_id.assert_called_once_with(
         project_id="linkpagamento",
    )


def test_deve_buscar_ambiente_pelo_environment_id():
    """
    Deve utilizar o environment_id informado para
    buscar o ambiente no repositório.
    """

    project = create_project()

    environment = create_environment()

    project_repository = MagicMock(
        spec=ProjectRepository,
    )

    environment_repository = MagicMock(
        spec=EnvironmentRepository,
    )

    project_repository.get_by_id.return_value = (
        project
    )

    environment_repository.get_by_id.return_value = (
        environment
    )

    resolver = create_resolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    resolver.resolve(
        project_id="linkpagamento",
        environment_id="producao",
    )

    environment_repository.get_by_id.assert_called_once_with(
        environment_id="producao",
    )


def test_deve_rejeitar_projeto_nao_encontrado():
    """
    Deve rejeitar a resolução quando o projeto
    não existir.
    """

    project_repository = MagicMock(
        spec=ProjectRepository,
    )

    environment_repository = MagicMock(
        spec=EnvironmentRepository,
    )

    project_repository.get_by_id.return_value = (
        None
    )

    resolver = create_resolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    with pytest.raises(
        Exception,
    ):
        resolver.resolve(
            project_id="projeto_inexistente",
            environment_id="producao",
        )

    environment_repository.get_by_id.assert_not_called()


def test_deve_rejeitar_ambiente_nao_encontrado():
    """
    Deve rejeitar a resolução quando o ambiente
    não existir.
    """

    project = create_project()

    project_repository = MagicMock(
        spec=ProjectRepository,
    )

    environment_repository = MagicMock(
        spec=EnvironmentRepository,
    )

    project_repository.get_by_id.return_value = (
        project
    )

    environment_repository.get_by_id.return_value = (
        None
    )

    resolver = create_resolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    with pytest.raises(
        Exception,
    ):
        resolver.resolve(
            project_id="linkpagamento",
            environment_id="ambiente_inexistente",
        )