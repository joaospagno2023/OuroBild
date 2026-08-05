"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_workspace_resolver.py
Descrição : Testes do WorkspaceResolver.
--------------------------------------------------------------------
"""
import pytest

from pathlib import Path
from unittest.mock import Mock

from app.models.build.compilation_engine import CompilationEngine
from app.models.build.compilation_target import CompilationTarget
from app.models.environment.build_environment import BuildEnvironment
from app.models.project.project import Project
from app.workspace.workspace_resolver import WorkspaceResolver
from app.exceptions.project_not_found_exception import (ProjectNotFoundException,)
from app.exceptions.environment_not_found_exception import (EnvironmentNotFoundException,)

def test_should_resolve_workspace():
    """
    Deve resolver corretamente um Workspace.
    """

    #
    # Arrange
    #

    project_repository = Mock()

    environment_repository = Mock()

    project = Project(
        id="erp",
        name="ERP",
        description="Projeto ERP",

        solution_path=None,

        project_path="src/erp/erp.csproj",

        compilation_target=CompilationTarget.PROJECT,

        compilation_engine=CompilationEngine.MSBUILD,

        publish_path="publish",

        aip_path="setup.aip",

        output_msi="erp.msi",

        network_path="\\\\server\\erp",

        configuration="Release",

        platform="AnyCPU",

        enabled=True,
    )

    environment = BuildEnvironment(
        id="production",
        name="Produção",
        resolver="local",
        root_path=Path("C:/Workspace"),
    )

    project_repository.get_by_id.return_value = project

    environment_repository.get_by_id.return_value = environment

    resolver = WorkspaceResolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    #
    # Act
    #

    workspace = resolver.resolve(
        project_id="erp",
        environment_id="production",
    )

    #
    # Assert
    #

    assert workspace.project == project

    assert workspace.environment == environment

    assert workspace.project_file == (
        Path("C:/Workspace")
        / "src/erp/erp.csproj"
    )

    project_repository.get_by_id.assert_called_once_with(
        project_id="erp",
    )

    environment_repository.get_by_id.assert_called_once_with(
        environment_id="production",
    )
def test_should_raise_project_not_found():
    """
    Deve lançar ProjectNotFoundException
    quando o projeto não existir.
    """

    #
    # Arrange
    #

    project_repository = Mock()

    environment_repository = Mock()

    project_repository.get_by_id.return_value = None

    resolver = WorkspaceResolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    #
    # Act / Assert
    #

    with pytest.raises(ProjectNotFoundException):

        resolver.resolve(
            project_id="projeto-inexistente",
            environment_id="production",
        )

    project_repository.get_by_id.assert_called_once_with(
        project_id="projeto-inexistente",
    )
def test_should_raise_environment_not_found():
    """
    Deve lançar EnvironmentNotFoundException
    quando o ambiente não existir.
    """

    #
    # Arrange
    #

    project_repository = Mock()

    environment_repository = Mock()

    project = Project(
        id="erp",
        name="ERP",
        description="Projeto ERP",
        solution_path=None,
        project_path="src/erp/erp.csproj",
        compilation_target=CompilationTarget.PROJECT,
        compilation_engine=CompilationEngine.DOTNET,
        publish_path="publish",
        aip_path="setup.aip",
        output_msi="erp.msi",
        network_path="\\\\server\\erp",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )

    project_repository.get_by_id.return_value = project

    environment_repository.get_by_id.return_value = None

    resolver = WorkspaceResolver(
        project_repository=project_repository,
        environment_repository=environment_repository,
    )

    #
    # Act / Assert
    #

    with pytest.raises(EnvironmentNotFoundException):

        resolver.resolve(
            project_id="erp",
            environment_id="production",
        )

    environment_repository.get_by_id.assert_called_once_with(
        environment_id="production",
    )