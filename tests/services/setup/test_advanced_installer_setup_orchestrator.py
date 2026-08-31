"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_advanced_installer_setup_orchestrator.py
Descrição : Testes do fluxo de geração de Setup utilizando
            Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
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

from app.services.setup.setup_project_preparer import (
    SetupProjectPreparer,
)

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)

from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
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


def create_request() -> SetupRequest:
    """
    Cria uma solicitação de geração de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
    )


def create_project() -> Project:
    """
    Cria um projeto mínimo para os testes.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",
        type=ProjectType.CLIENT,
        solution_path=(
            r"C:\Projetos\Projeto\Projeto.sln"
        ),
        project_path=(
            r"C:\Projetos\Projeto\Projeto.csproj"
        ),
        compilation_target=(
            CompilationTarget.PROJECT
        ),
        compilation_engine=(
            CompilationEngine.MSBUILD
        ),
        publish_path=(
            r"C:\Projetos\Projeto"
            r"\bin\Release"
        ),
        publish_profile=None,
        aip_path=(
            r"C:\Projetos\Projeto"
            r"\Setup\Projeto.aip"
        ),
        visualstudio_setup_path=None,
        output_msi=(
            r"C:\Setups\Projeto.Setup.msi"
        ),
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_workspace_context() -> WorkspaceContext:
    """
    Cria o contexto de Workspace utilizado pelos testes.

    O objeto é criado como mock para que o teste fique
    isolado das implementações físicas de Workspace.
    """

    context = MagicMock(
        spec=WorkspaceContext,
    )

    context.project = create_project()

    return context


def create_paths() -> SetupPaths:
    """
    Cria os caminhos utilizados pelo Setup.
    """

    return SetupPaths(
        publish_path=Path(
            r"C:\Projetos\Projeto"
            r"\bin\Release"
        ),
        setup_output_path=Path(
            r"C:\Setups"
        ),
        output_msi=Path(
            r"C:\Setups\Projeto.Setup.msi"
        ),
        aip_path=Path(
            r"C:\Projetos\Projeto"
            r"\Setup\Projeto.aip"
        ),
        visualstudio_setup_path=None,
    )


def create_definition(
    paths: SetupPaths,
) -> SetupDefinition:
    """
    Cria uma definição de Setup para
    Advanced Installer.
    """

    return SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Projeto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=Path(
            r"C:\Projetos\Projeto"
            r"\Projeto.sln"
        ),
        setup_project_path=(
            paths.aip_path
        ),
        output_msi=(
            paths.output_msi
        ),
    )


def create_orchestrator(
    workspace_resolver,
    setup_path_resolver,
    solution_locator,
    definition_loader,
    advanced_installer_definition_loader,
    setup_factory,
    setup_project_preparer=None,
    setup_workspace_service=None,
):
    """
    Cria o DefaultSetupOrchestrator utilizando
    a arquitetura atual do fluxo de Setup.

    As dependências antigas relacionadas ao fluxo
    Visual Studio continuam na assinatura para manter
    os testes compatíveis, mas não são mais injetadas
    no DefaultSetupOrchestrator.

    O Orchestrator atual recebe:

        - WorkspaceResolver;
        - SetupPathResolver;
        - AdvancedInstallerSetupDefinitionLoader;
        - SetupFactory;
        - AppSettings.
    """

    settings = MagicMock()

    settings.setup = MagicMock()

    settings.setup.engine = (
        SetupEngine.ADVANCED_INSTALLER
    )

    settings.setup.output_root = Path(
        r"C:\Setups"
    )

    settings.setup.aip_root = Path(
        r"C:\Projetos\Projeto\Setup"
    )

    return DefaultSetupOrchestrator(
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

# ====================================================================
# Testes
# ====================================================================


def test_deve_executar_setup_advanced_installer():
    """
    Deve executar o fluxo completo utilizando
    Advanced Installer.

    O fluxo Advanced Installer deve:

        - resolver o Workspace;
        - resolver os caminhos;
        - carregar a definição AIP;
        - selecionar Advanced Installer;
        - executar o InstallerService.

    Não deve:

        - procurar Solution Visual Studio;
        - utilizar o loader Visual Studio.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition(
        paths,
    )

    expected_result = SetupResult(
        success=True,
        message="Setup gerado com sucesso.",
        project_id="teste",
        output_msi=(
            paths.output_msi
        ),
        duration_seconds=3.0,
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    installer.install.return_value = (
        expected_result
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    setup_factory.create.return_value = (
        installer
    )

    setup_project_preparer = MagicMock(
        spec=SetupProjectPreparer,
    )

    setup_workspace_service = MagicMock(
        spec=SetupWorkspaceService,
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
        setup_project_preparer=(
            setup_project_preparer
        ),
        setup_workspace_service=(
            setup_workspace_service
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result is expected_result

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )

    advanced_installer_definition_loader.load.assert_called_once()

    visual_studio_definition_loader.load.assert_not_called()

    solution_locator.find_solution.assert_not_called()

    setup_factory.create.assert_called_once_with(
        SetupEngine.ADVANCED_INSTALLER,
    )

    installer.install.assert_called_once()


def test_deve_nao_utilizar_loader_visual_studio_no_advanced_installer():
    """
    Deve utilizar exclusivamente o loader do
    Advanced Installer quando o engine configurado
    for ADVANCED_INSTALLER.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition(
        paths,
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    installer.install.return_value = SetupResult(
        success=True,
        message="OK",
        project_id="teste",
        output_msi=(
            paths.output_msi
        ),
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    setup_factory.create.return_value = (
        installer
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result.success is True

    advanced_installer_definition_loader.load.assert_called_once()

    visual_studio_definition_loader.load.assert_not_called()

    solution_locator.find_solution.assert_not_called()

    setup_factory.create.assert_called_once_with(
        SetupEngine.ADVANCED_INSTALLER,
    )

    installer.install.assert_called_once()


def test_deve_retornar_falha_quando_loader_advanced_installer_falhar():
    """
    Deve retornar falha quando o loader do
    Advanced Installer gerar uma exceção.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.side_effect = (
        ValueError(
            "Definition inválida."
        )
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    setup_factory.create.return_value = (
        installer
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result.success is False

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi is None

    assert (
        "Definition inválida."
        in result.message
    )

    installer.install.assert_not_called()

    setup_factory.create.assert_not_called()

    visual_studio_definition_loader.load.assert_not_called()

    solution_locator.find_solution.assert_not_called()


def test_deve_retornar_resultado_do_advanced_installer():
    """
    Deve retornar exatamente o resultado produzido
    pelo InstallerService.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition(
        paths,
    )

    expected_result = SetupResult(
        success=False,
        message="Falha ao gerar Setup.",
        project_id="teste",
        output_msi=None,
        duration_seconds=4.0,
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    installer.install.return_value = (
        expected_result
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    setup_factory.create.return_value = (
        installer
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result is expected_result

    assert result.success is False

    assert result.output_msi is None

    assert result.duration_seconds == (
        4.0
    )

    installer.install.assert_called_once()


def test_deve_nao_procurar_solution_no_fluxo_advanced_installer():
    """
    O fluxo Advanced Installer não deve procurar
    uma Solution do Visual Studio.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition(
        paths,
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    installer.install.return_value = SetupResult(
        success=True,
        message="OK",
        project_id="teste",
        output_msi=(
            paths.output_msi
        ),
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    setup_factory.create.return_value = (
        installer
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result.success is True

    solution_locator.find_solution.assert_not_called()

    visual_studio_definition_loader.load.assert_not_called()

    advanced_installer_definition_loader.load.assert_called_once()


def test_deve_resolver_workspace_antes_de_gerar_setup():
    """
    Deve resolver o Workspace antes de executar
    o fluxo de geração do Setup.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition(
        paths,
    )

    workspace_resolver = MagicMock(
        spec=WorkspaceResolver,
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    solution_locator = MagicMock(
        spec=SolutionLocatorService,
    )

    visual_studio_definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )

    advanced_installer_definition_loader.load.return_value = (
        definition
    )

    installer = MagicMock(
        spec=InstallerService,
    )

    installer.install.return_value = SetupResult(
        success=True,
        message="OK",
        project_id="teste",
        output_msi=(
            paths.output_msi
        ),
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
    )

    setup_factory.create.return_value = (
        installer
    )

    orchestrator = create_orchestrator(
        workspace_resolver=(
            workspace_resolver
        ),
        setup_path_resolver=(
            setup_path_resolver
        ),
        solution_locator=(
            solution_locator
        ),
        definition_loader=(
            visual_studio_definition_loader
        ),
        advanced_installer_definition_loader=(
            advanced_installer_definition_loader
        ),
        setup_factory=(
            setup_factory
        ),
    )

    result = orchestrator.execute(
        request,
    )

    assert result.success is True

    workspace_resolver.resolve.assert_called_once()

    setup_path_resolver.resolve.assert_called_once()

    advanced_installer_definition_loader.load.assert_called_once()

    installer.install.assert_called_once()