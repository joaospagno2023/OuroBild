"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_default_setup_orchestrator.py
Descrição : Testes do DefaultSetupOrchestrator utilizando
            exclusivamente o Advanced Installer.
--------------------------------------------------------------------
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.models.configuration.app_settings import AppSettings
from app.models.environment.build_environment import BuildEnvironment
from app.models.project.project import Project
from app.models.project.project_type import ProjectType
from app.models.setup.setup_definition import SetupDefinition
from app.models.setup.setup_engine import SetupEngine
from app.models.setup.setup_paths import SetupPaths
from app.models.setup.setup_request import SetupRequest
from app.models.setup.setup_result import SetupResult
from app.services.setup.advanced_installer_setup_definition_loader import (
    AdvancedInstallerSetupDefinitionLoader,
)
from app.services.setup.setup_factory import DefaultSetupFactory
from app.services.setup.setup_orchestrator import DefaultSetupOrchestrator
from app.services.setup.setup_path_resolver import SetupPathResolver
from app.workspace.workspace_context import WorkspaceContext
from app.workspace.workspace_resolver import WorkspaceResolver


def create_request() -> SetupRequest:
    """
    Cria uma solicitação mínima de Setup.
    """
    return SetupRequest(
        project_id='teste',
        environment_id='producao',
        version='1.0.0',
        revision=1
    )


def create_project() -> Project:
    """
    Cria um projeto mínimo para os testes.
    """
    return Project(
        id='teste',
        name='Projeto Teste',
        description='Projeto utilizado nos testes.',
        type=ProjectType.CLIENT,
        solution_path=None,
        project_path='Projeto.csproj',
        compilation_target='project',
        compilation_engine='msbuild',
        publish_path='bin\\Release\\publish',
        publish_profile=None,
        aip_path='Setup\\Teste.aip',
        visualstudio_setup_path=None,
        output_msi='Teste.msi',
        network_path='',
        configuration='Release',
        platform='AnyCPU',
        enabled=True
    )


def create_environment() -> BuildEnvironment:
    """
    Cria um ambiente mínimo para os testes.
    """
    return BuildEnvironment(
        id='producao',
        name='Produção',
        root_path=Path('C:\\Projetos'),
        resolver='static'
    )


def create_workspace_context() -> WorkspaceContext:
    """
    Cria um WorkspaceContext mínimo.
    """
    return WorkspaceContext(
        project=create_project(),
        environment=create_environment(),
        project_file=Path('C:\\Projetos\\Projeto\\Projeto.csproj')
    )


def create_paths() -> SetupPaths:
    """
    Cria caminhos mínimos para o Setup.

    O modelo SetupPaths utiliza setup_output_path,
    e não installer_path.
    """
    return SetupPaths(
        publish_path=Path('C:\\Projetos\\Projeto\\bin\\Release\\publish'),
        setup_output_path=Path('C:\\Installers'),
        output_msi=Path('C:\\Installers\\Teste.msi'),
        aip_path=Path('C:\\Projetos\\Projeto\\Setup\\Teste.aip'),
        visualstudio_setup_path=None
    )


def create_definition(paths: SetupPaths) -> SetupDefinition:
    """
    Cria uma definição mínima de Setup Advanced Installer.
    """
    return SetupDefinition(
        project_id='teste',
        name='Projeto Teste',
        product_name='Produto Teste',
        manufacturer='Custom Software',
        version='1.0.0',
        configuration='Release',
        platform='AnyCPU',
        solution_path=Path('C:\\Projetos\\Projeto\\Projeto.sln'),
        setup_project_path=paths.aip_path,
        output_msi=paths.output_msi
    )


def create_settings() -> AppSettings:
    """
    Cria uma configuração mínima utilizando
    exclusivamente Advanced Installer.
    """
    settings = MagicMock(spec=AppSettings)
    settings.setup = MagicMock()
    settings.setup.engine = SetupEngine.ADVANCED_INSTALLER
    settings.setup.output_root = Path('C:\\Installers')
    settings.setup.aip_root = Path('C:\\Projetos\\Projetos')
    return settings


def create_orchestrator(
    workspace_resolver,
    setup_path_resolver,
    advanced_installer_definition_loader,
    setup_factory,
    settings=None
):
    """
    Cria o DefaultSetupOrchestrator utilizando
    somente as dependências do fluxo Advanced Installer.
    """
    if settings is None:
        settings = create_settings()
    return DefaultSetupOrchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory,
        settings=settings
    )


def create_mocks():
    """
    Cria os mocks comuns utilizados pelos testes.
    """
    workspace_resolver = MagicMock(spec=WorkspaceResolver)
    setup_path_resolver = MagicMock(spec=SetupPathResolver)
    advanced_installer_definition_loader = MagicMock(
        spec=AdvancedInstallerSetupDefinitionLoader,
    )
    setup_factory = MagicMock(spec=DefaultSetupFactory)
    installer = MagicMock()
    return (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer
    )


def test_deve_executar_setup_advanced_installer():
    """
    Deve executar o fluxo completo utilizando
    exclusivamente Advanced Installer.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    definition = create_definition(paths)
    expected_result = SetupResult(
        success=True,
        message='Setup gerado com sucesso.',
        project_id='teste',
        output_msi=paths.output_msi,
        duration_seconds=3.0
    )
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.return_value = definition
    installer.install.return_value = expected_result
    setup_factory.create.return_value = installer
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result is expected_result
    workspace_resolver.resolve.assert_called_once_with(
        project_id='teste',
        environment_id='producao'
    )
    setup_path_resolver.resolve.assert_called_once()
    advanced_installer_definition_loader.load.assert_called_once_with(
        aip_path=paths.aip_path,
        project_id='teste',
        configuration='Release',
        platform='AnyCPU',
        output_msi=paths.output_msi
    )
    setup_factory.create.assert_called_once_with(SetupEngine.ADVANCED_INSTALLER)
    installer.install.assert_called_once_with(
        request=request,
        definition=definition,
        paths=paths
    )


def test_deve_utilizar_loader_advanced_installer():
    """
    Deve utilizar exclusivamente o loader do
    Advanced Installer.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    definition = create_definition(paths)
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.return_value = definition
    installer.install.return_value = SetupResult(
        success=True,
        message='OK',
        project_id='teste',
        output_msi=paths.output_msi
    )
    setup_factory.create.return_value = installer
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result.success is True
    advanced_installer_definition_loader.load.assert_called_once()
    setup_factory.create.assert_called_once_with(SetupEngine.ADVANCED_INSTALLER)
    installer.install.assert_called_once()


def test_deve_retornar_falha_quando_loader_advanced_installer_falhar():
    """
    Deve retornar falha quando o loader do
    Advanced Installer gerar uma exceção.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.side_effect = ValueError(
        "Definition inválida."
    )
    setup_factory.create.return_value = installer
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result.success is False
    assert 'Definition inválida.' in result.message
    installer.install.assert_not_called()
    setup_factory.create.assert_not_called()


def test_deve_retornar_falha_quando_workspace_nao_puder_ser_resolvido():
    """
    Deve retornar falha quando o Workspace
    não puder ser resolvido.
    """
    request = create_request()
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.side_effect = ValueError('Workspace inválido.')
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result.success is False
    assert 'Workspace inválido.' in result.message
    setup_path_resolver.resolve.assert_not_called()
    advanced_installer_definition_loader.load.assert_not_called()
    setup_factory.create.assert_not_called()


def test_deve_retornar_falha_quando_setup_path_nao_puder_ser_resolvido():
    """
    Deve retornar falha quando os caminhos do
    Setup não puderem ser resolvidos.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.side_effect = ValueError('Caminhos do Setup inválidos.')
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result.success is False
    assert 'Caminhos do Setup inválidos.' in result.message
    advanced_installer_definition_loader.load.assert_not_called()
    setup_factory.create.assert_not_called()


def test_deve_retornar_resultado_do_instalador_advanced_installer():
    """
    Deve retornar exatamente o SetupResult produzido
    pelo InstallerService.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    definition = create_definition(paths)
    expected_result = SetupResult(
        success=False,
        message='Falha ao gerar Setup.',
        project_id='teste',
        output_msi=None,
        duration_seconds=4.0
    )
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.return_value = definition
    installer.install.return_value = expected_result
    setup_factory.create.return_value = installer
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result is expected_result


def test_deve_passar_request_definition_e_paths_para_installer():
    """
    Deve passar para o InstallerService exatamente
    os objetos Request, Definition e Paths.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    definition = create_definition(paths)
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.return_value = definition
    installer.install.return_value = SetupResult(
        success=True,
        message='OK',
        project_id='teste',
        output_msi=paths.output_msi
    )
    setup_factory.create.return_value = installer
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    result = orchestrator.execute(request)
    assert result.success is True
    call = installer.install.call_args
    assert call is not None
    assert call.kwargs['request'] is request
    assert call.kwargs['definition'] is definition
    assert call.kwargs['paths'] is paths


def test_deve_rejeitar_request_nulo():
    """
    Deve rejeitar uma solicitação nula.
    """
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory
    )
    with pytest.raises(ValueError, match='SetupRequest não foi informado'):
        orchestrator.execute(None)


def test_deve_criar_instalador_com_engine_advanced_installer():
    """
    Deve selecionar explicitamente o engine
    Advanced Installer.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    paths = create_paths()
    definition = create_definition(paths)
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    setup_path_resolver.resolve.return_value = paths
    advanced_installer_definition_loader.load.return_value = definition
    installer.install.return_value = SetupResult(
        success=True,
        message='OK',
        project_id='teste',
        output_msi=paths.output_msi
    )
    setup_factory.create.return_value = installer
    settings = create_settings()
    settings.setup.engine = SetupEngine.ADVANCED_INSTALLER.value
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory,
        settings=settings
    )
    result = orchestrator.execute(request)
    assert result.success is True
    setup_factory.create.assert_called_once_with(SetupEngine.ADVANCED_INSTALLER)


def test_deve_rejeitar_engine_nao_suportado():
    """
    Deve rejeitar qualquer engine diferente de
    Advanced Installer.
    """
    request = create_request()
    workspace_context = create_workspace_context()
    (
        workspace_resolver,
        setup_path_resolver,
        advanced_installer_definition_loader,
        setup_factory,
        installer,
    ) = create_mocks()
    workspace_resolver.resolve.return_value = workspace_context
    settings = create_settings()
    settings.setup.engine = 'visual_studio'
    orchestrator = create_orchestrator(
        workspace_resolver=workspace_resolver,
        setup_path_resolver=setup_path_resolver,
        advanced_installer_definition_loader=advanced_installer_definition_loader,
        setup_factory=setup_factory,
        settings=settings
    )
    result = orchestrator.execute(request)
    assert result.success is False
    assert 'Advanced Installer' in result.message
    setup_path_resolver.resolve.assert_not_called()
    advanced_installer_definition_loader.load.assert_not_called()
    setup_factory.create.assert_not_called()
