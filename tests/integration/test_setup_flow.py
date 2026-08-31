"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_flow.py
Descrição : Teste de integração do fluxo completo de Setup
            utilizando exclusivamente o Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.project.project import (
    Project,
)

from app.models.project.project_type import (
    ProjectType,
)

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.services.setup.advanced_installer_setup_definition_loader import (
    AdvancedInstallerSetupDefinitionLoader,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)

from app.workspace.workspace_context import (
    WorkspaceContext,
)

from app.workspace.workspace_resolver import (
    WorkspaceResolver,
)


# ====================================================================
# Helpers
# ====================================================================


def create_project(
    tmp_path: Path,
) -> Project:
    """
    Cria um projeto mínimo para o teste.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description=(
            "Projeto utilizado no teste de integração."
        ),
        type=ProjectType.CLIENT,
        solution_path=str(
            tmp_path
            / "Projeto.sln"
        ),
        project_path=str(
            tmp_path
            / "Projeto.csproj"
        ),
        compilation_target="project",
        compilation_engine="msbuild",
        publish_path=str(
            tmp_path
            / "publish"
        ),
        publish_profile=None,
        aip_path=str(
            tmp_path
            / "Setup"
            / "Teste.aip"
        ),
        visualstudio_setup_path=None,
        output_msi=str(
            tmp_path
            / "installer"
            / "Teste.msi"
        ),
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_solution(
    solution_path: Path,
) -> None:
    """
    Cria uma Solution mínima para o teste.
    """

    solution_path.write_text(
        """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
""".strip(),
        encoding="utf-8",
    )


def create_project_file(
    project_path: Path,
) -> None:
    """
    Cria um projeto mínimo para o teste.
    """

    project_path.write_text(
        """
<Project>
    <PropertyGroup>
        <TargetFramework>net8.0</TargetFramework>
    </PropertyGroup>
</Project>
""".strip(),
        encoding="utf-8",
    )


def create_workspace_context(
    tmp_path: Path,
) -> WorkspaceContext:
    """
    Cria o WorkspaceContext utilizado pelo teste.
    """

    project = create_project(
        tmp_path=tmp_path,
    )

    create_project_file(
        Path(
            project.project_path,
        ),
    )

    create_solution(
        Path(
            project.solution_path,
        ),
    )

    return WorkspaceContext(
        project=project,
        environment=MagicMock(
            root_path=tmp_path,
        ),
        project_file=Path(
            project.project_path,
        ),
    )


def create_paths(
    tmp_path: Path,
) -> SetupPaths:
    """
    Cria os caminhos utilizados pelo Setup.
    """

    publish_path = (
        tmp_path
        / "publish"
    )

    setup_output_path = (
        tmp_path
        / "installer"
    )

    aip_path = (
        tmp_path
        / "Setup"
        / "Teste.aip"
    )

    output_msi = (
        setup_output_path
        / "Teste.msi"
    )

    publish_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    aip_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return SetupPaths(
        publish_path=publish_path,
        setup_output_path=setup_output_path,
        output_msi=output_msi,
        aip_path=aip_path,
        visualstudio_setup_path=None,
    )


def create_definition(
    paths: SetupPaths,
    solution_path: Path,
) -> SetupDefinition:
    """
    Cria uma definição mínima do Advanced Installer.
    """

    return SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Produto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=solution_path,
        setup_project_path=paths.aip_path,
        output_msi=paths.output_msi,
    )


def create_request() -> SetupRequest:
    """
    Cria a solicitação de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
        configuration="Release",
    )


# ====================================================================
# Teste de integração
# ====================================================================


def test_deve_executar_fluxo_completo_de_setup_advanced_installer(
    tmp_path: Path,
):
    """
    Deve executar o fluxo completo de Setup utilizando
    exclusivamente o Advanced Installer.

    O processo externo real não é executado.

    O teste valida a integração entre:

        WorkspaceResolver
            ↓
        SetupPathResolver
            ↓
        AdvancedInstallerSetupDefinitionLoader
            ↓
        SetupFactory
            ↓
        InstallerService
            ↓
        SetupResult
    """

    #
    # ================================================================
    # Request
    # ================================================================
    #

    request = create_request()

    #
    # ================================================================
    # Workspace
    # ================================================================
    #

    workspace_context = (
        create_workspace_context(
            tmp_path=tmp_path,
        )
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    #
    # ================================================================
    # Paths
    # ================================================================
    #

    paths = create_paths(
        tmp_path=tmp_path,
    )

    setup_path_resolver = MagicMock(
    spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    #
    # ================================================================
    # AIP
    # ================================================================
    #

    paths.aip_path.write_text(
        """
; OuroBuild integration test
""".strip(),
        encoding="utf-8",
    )

    #
    # ================================================================
    # Advanced Installer Definition
    # ================================================================
    #

    solution_path = Path(
        workspace_context.project.solution_path,
    )

    definition = create_definition(
        paths=paths,
        solution_path=solution_path,
    )

    advanced_installer_definition_loader = (
        MagicMock(
            spec=AdvancedInstallerSetupDefinitionLoader,
        )
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    #
    # ================================================================
    # Installer
    # ================================================================
    #

    installer = MagicMock(
        spec=InstallerService,
    )

    expected_result = SetupResult(
        success=True,
        message="Setup gerado com sucesso.",
        project_id="teste",
        output_msi=paths.output_msi,
        duration_seconds=2.0,
    )

    installer.install.return_value = (
        expected_result
    )

    #
    # ================================================================
    # Factory
    # ================================================================
    #

    setup_factory = DefaultSetupFactory(
        visual_studio_installer=MagicMock(
            spec=InstallerService,
        ),
        advanced_installer=installer,
    )

    #
    # ================================================================
    # Settings
    # ================================================================
    #

    settings = MagicMock()

    settings.setup = MagicMock()

    settings.setup.engine = (
        SetupEngine.ADVANCED_INSTALLER
    )

    settings.setup.output_root = (
        tmp_path
        / "installer"
    )

    settings.setup.aip_root = (
        tmp_path
        / "Setup"
    )

    #
    # ================================================================
    # Orchestrator
    # ================================================================
    #

    orchestrator = DefaultSetupOrchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
        settings=settings,
    )

    #
    # ================================================================
    # Execução
    # ================================================================
    #

    result = orchestrator.execute(
        request,
    )

    #
    # ================================================================
    # Resultado
    # ================================================================
    #

    assert result is expected_result

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )

    #
    # ================================================================
    # Workspace
    # ================================================================
    #

    workspace_resolver.resolve.assert_called_once_with(
        project_id="teste",
        environment_id="producao",
    )

    #
    # ================================================================
    # Setup Path Resolver
    # ================================================================
    #

    setup_path_resolver.resolve.assert_called_once()

    #
    # ================================================================
    # Definition Loader
    # ================================================================
    #

    advanced_installer_definition_loader.load.assert_called_once_with(
        aip_path=paths.aip_path,
        project_id="teste",
        configuration="Release",
        platform="AnyCPU",
        output_msi=paths.output_msi,
    )

    #
    # ================================================================
    # Installer
    # ================================================================
    #

    installer.install.assert_called_once_with(
        request=request,
        definition=definition,
        paths=paths,
    )