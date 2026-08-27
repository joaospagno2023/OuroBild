"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_default_setup_orchestrator.py
Descrição : Testes do DefaultSetupOrchestrator.
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

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.environment.build_environment import (
    BuildEnvironment,
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


def create_request() -> SetupRequest:
    """
    Cria uma solicitação mínima de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
    )


def create_paths() -> SetupPaths:
    """
    Cria caminhos mínimos para o Setup.
    """

    return SetupPaths(
        publish_path=Path(
            r"C:\Projetos\Projeto"
            r"\bin\Release\publish"
        ),
        setup_output_path=Path(
            r"C:\Installers"
        ),
        output_msi=Path(
            r"C:\Installers\Teste.msi"
        ),
        aip_path=Path(
            r"C:\Projetos\Projeto"
            r"\Setup\Teste.aip"
        ),
    )


def create_environment() -> BuildEnvironment:
    """
    Cria um ambiente mínimo para os testes.
    """

    return BuildEnvironment(
        id="producao",
        name="Produção",
        root_path=Path(
            r"C:\Projetos"
        ),
        resolver="static",
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
        publish_path="publish",
        aip_path=(
            r"Setup\Projeto.vdproj"
        ),
        output_msi="Projeto.msi",
        network_path="",
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_workspace_context() -> WorkspaceContext:
    """
    Cria um WorkspaceContext mínimo.
    """

    return WorkspaceContext(
        project=create_project(),
        environment=create_environment(),
        project_file=Path(
            r"C:\Projetos\Projeto\Projeto.csproj"
        ),
    )


def create_definition() -> SetupDefinition:
    """
    Cria uma definição mínima de Setup.
    """

    return SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Produto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=Path(
            r"C:\Projetos\Projeto\Projeto.sln"
        ),
        setup_project_path=Path(
            r"C:\Projetos\Projeto"
            r"\Setup\Teste.aip"
        ),
        output_msi=Path(
            r"C:\Installers\Teste.msi"
        ),
    )


def create_settings() -> AppSettings:
    """
    Cria uma configuração mínima para os testes.
    """

    settings = MagicMock(
        spec=AppSettings,
    )

    #
    # Configuração antiga.
    #
    # Mantida porque outros componentes do
    # AppSettings ainda podem utilizá-la.
    #

    settings.installer_path = (
        Path(r"C:\Installers")
    )

    #
    # Configuração de Setup.
    #

    settings.setup = MagicMock()

    settings.setup.engine = (
        SetupEngine.VISUAL_STUDIO
    )

    settings.setup.output_root = (
        Path(r"C:\Setups")
    )

    settings.setup.aip_root = (
        Path(
            r"C:\DvpLocal\WorkSpaceTFS"
            r"\Transferencia de Arquivo"
            r"\TransferenciaDeArquivos"
            r"\Setups\Installers\Projects"
        )
    )

    return settings


def create_orchestrator(
    workspace_resolver,
    setup_path_resolver,
    solution_locator,
    definition_loader,
    setup_factory,
    setup_project_preparer=None,
    setup_workspace_service=None,
):
    """
    Cria o Orchestrator com suas dependências.

    O SetupProjectPreparer é opcional no helper para manter
    os testes existentes compatíveis com cenários que não
    utilizam preparação de projeto Visual Studio Setup.

    O SetupWorkspaceService é opcional para manter os testes
    simples e permitir que cada cenário utilize o mock
    necessário.
    """

    if setup_project_preparer is None:

        setup_project_preparer = MagicMock(
            spec=SetupProjectPreparer,
        )

    if setup_workspace_service is None:

        setup_workspace_service = MagicMock(
            spec=SetupWorkspaceService,
        )

    return DefaultSetupOrchestrator(
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
            definition_loader
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
        settings=create_settings(),
    )


def test_deve_executar_setup_visual_studio():
    """
    Deve executar o fluxo completo do Setup
    utilizando Visual Studio.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    definition = create_definition()

    expected_result = SetupResult(
        success=True,
        message="Setup gerado com sucesso.",
        project_id="teste",
        output_msi=paths.output_msi,
        duration_seconds=1.0,
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

    solution_locator.find_solution.return_value = (
        definition.solution_path
    )

    definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    definition_loader.load.return_value = (
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
            definition_loader
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

    workspace_resolver.resolve.assert_called_once_with(
        project_id="teste",
        environment_id="producao",
    )

    setup_path_resolver.resolve.assert_called_once_with(
        project=workspace_context.project,
        project_root=(
            workspace_context.project_file.parent
        ),
        workspace_root=(
            workspace_context.environment.root_path
        ),
        installer_root=Path(
            r"C:\Setups"
        ),
        aip_root=(
            Path(
                r"C:\DvpLocal\WorkSpaceTFS"
                r"\Transferencia de Arquivo"
                r"\TransferenciaDeArquivos"
                r"\Setups\Installers\Projects"
            )
        ),
        version="1.0.0",
        revision=1,
    )

    solution_locator.find_solution.assert_called_once_with(
        workspace_context.project_file,
    )

    definition_loader.load.assert_called_once_with(
        setup_project_path=(
            paths.aip_path
        ),
        solution_path=(
            definition.solution_path
        ),
        configuration="Release",
        platform="AnyCPU",
    )

    setup_factory.create.assert_called_once_with(
        SetupEngine.VISUAL_STUDIO,
    )

    installer.install.assert_called_once_with(
        request=request,
        definition=definition,
        paths=paths,
    )

    #
    # Como este teste utiliza AIP e não .vdproj,
    # o preparador não deve ser executado.
    #

    setup_project_preparer.prepare.assert_not_called()

    setup_workspace_service.backup_original.assert_not_called()

    setup_workspace_service.replace_original.assert_not_called()

    setup_workspace_service.restore_original.assert_not_called()

    setup_workspace_service.cleanup.assert_not_called()


def test_deve_retornar_falha_quando_solution_nao_for_encontrada():
    """
    Deve retornar falha quando a Solution não for encontrada.
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

    solution_locator.find_solution.return_value = (
        None
    )

    definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
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
            definition_loader
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

    assert result.success is False

    assert result.project_id == (
        "teste"
    )

    assert "Solution" in (
        result.message
    )

    definition_loader.load.assert_not_called()

    setup_factory.create.assert_not_called()

    setup_project_preparer.prepare.assert_not_called()

    setup_workspace_service.backup_original.assert_not_called()

    setup_workspace_service.replace_original.assert_not_called()

    setup_workspace_service.restore_original.assert_not_called()

    setup_workspace_service.cleanup.assert_not_called()


def test_deve_nao_executar_instalador_quando_definition_falhar():
    """
    Deve interromper o fluxo quando a definição
    do Setup não puder ser carregada.
    """

    request = create_request()

    workspace_context = (
        create_workspace_context()
    )

    paths = create_paths()

    solution_path = Path(
        r"C:\Projetos\Projeto\Projeto.sln"
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

    solution_locator.find_solution.return_value = (
        solution_path
    )

    definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    definition_loader.load.side_effect = (
        ValueError(
            "Definition inválida."
        )
    )

    setup_factory = MagicMock(
        spec=DefaultSetupFactory,
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
            definition_loader
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

    assert result.success is False

    assert result.project_id == (
        "teste"
    )

    assert (
        "Definition inválida."
        in result.message
    )

    setup_factory.create.assert_not_called()

    setup_project_preparer.prepare.assert_not_called()

    setup_workspace_service.backup_original.assert_not_called()

    setup_workspace_service.replace_original.assert_not_called()

    setup_workspace_service.restore_original.assert_not_called()

    setup_workspace_service.cleanup.assert_not_called()