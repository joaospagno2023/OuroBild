"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_flow.py
Descrição : Teste de integração do fluxo completo de Setup.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.process.process_status import (
    ProcessStatus,
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

from app.services.setup.disable_out_of_proc_build_service import (
    DisableOutOfProcBuildService,
)

from app.services.setup.setup_factory import (
    DefaultSetupFactory,
)

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)

from app.services.setup.setup_project_preparer import (
    SetupProjectPreparer,
)

from app.services.setup.setup_path_resolver import (
    SetupPathResolver,
)

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.visual_studio_installer_service import (
    VisualStudioInstallerService,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)


def create_project_file(
    path: Path,
) -> None:
    """
    Cria um projeto mínimo para o teste.
    """

    path.write_text(
        """
<Project>
    <PropertyGroup>
        <TargetFramework>net8.0</TargetFramework>
    </PropertyGroup>
</Project>
""".strip(),
        encoding="utf-8",
    )


def create_solution(
    solution_path: Path,
    project_path: Path,
) -> None:
    """
    Cria uma Solution mínima para o teste.
    """

    solution_path.write_text(
        f"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
Project("{{FAKE-GUID}}") = "Projeto", "{project_path.name}", "{{PROJECT-GUID}}"
EndProject
""".strip(),
        encoding="utf-8",
    )


def test_deve_executar_fluxo_completo_de_setup_visual_studio(
    tmp_path: Path,
):
    """
    Deve executar o fluxo completo do Setup utilizando
    Visual Studio sem executar o processo externo real.
    """

    #
    # Request
    #

    request = SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
        configuration="Release",
    )

    #
    # Diretórios
    #

    publish_path = (
        tmp_path
        / "publish"
    )

    setup_output_path = (
        tmp_path
        / "installer"
    )

    setup_path = (
        tmp_path
        / "Setup"
    )

    publish_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # Arquivos do projeto
    #

    project_file = (
        tmp_path
        / "Projeto.csproj"
    )

    solution_file = (
        tmp_path
        / "Projeto.sln"
    )

    setup_project_file = (
        setup_path
        / "Teste.vdproj"
    )

    create_project_file(
        project_file,
    )

    create_solution(
        solution_path=solution_file,
        project_path=project_file,
    )

    setup_project_file.write_text(
        """
"FileSystem"
{
    "DefaultLocation" = "8:[ProgramFilesFolder][Manufacturer]\\[ProductName]"

    "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Teste, Version=1.0.0.0"

        "ScatterAssemblies"
        {
            "_111111"
            {
                "Name" = "8:Teste.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Teste.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_AAAAAA"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
""".strip(),
        encoding="utf-8",
    )

    #
    # Setup Paths
    #

    paths = SetupPaths(
        publish_path=publish_path,
        setup_output_path=setup_output_path,
        output_msi=(
            setup_output_path
            / "Teste.msi"
        ),
        aip_path=setup_project_file,
        visualstudio_setup_path=(
            setup_project_file
        ),
    )

    #
    # Setup Definition
    #

    definition = SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Produto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=solution_file,
        setup_project_path=setup_project_file,
        output_msi=(
            setup_output_path
            / "Teste.msi"
        ),
    )

    #
    # Workspace
    #

    workspace_resolver = MagicMock()

    workspace_context = MagicMock()

    workspace_context.project = (
        MagicMock()
    )

    workspace_context.project.id = (
        "teste"
    )

    workspace_context.project.publish_path = (
        "publish"
    )

    workspace_context.project.aip_path = (
        r"Setup\Teste.vdproj"
    )

    workspace_context.project.output_msi = (
        "Teste.msi"
    )

    workspace_context.project.configuration = (
        "Release"
    )

    workspace_context.project.platform = (
        "AnyCPU"
    )

    workspace_context.project_file = (
        project_file
    )

    workspace_context.environment = (
        MagicMock()
    )

    workspace_context.environment.root_path = (
        tmp_path
    )

    workspace_resolver.resolve.return_value = (
        workspace_context
    )

    #
    # Setup Path Resolver
    #

    setup_path_resolver = MagicMock(
        spec=SetupPathResolver,
    )

    setup_path_resolver.resolve.return_value = (
        paths
    )

    #
    # Solution Locator
    #

    solution_locator = MagicMock()

    solution_locator.find_solution.return_value = (
        solution_file
    )

    #
    # Definition Loader
    #

    definition_loader = MagicMock(
        spec=VisualStudioSetupDefinitionLoader,
    )

    definition_loader.load.return_value = (
        definition
    )

    #
    # Setup Project Preparer
    #

    # O teste não executa a preparação real.
    # Simulamos o retorno de um projeto preparado.
    #

    setup_project_preparer = MagicMock(
        spec=SetupProjectPreparer,
    )

    prepared_setup_file = (
        setup_path
        / ".ourobuild"
        / "Teste.vdproj"
    )

    prepared_setup_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    prepared_setup_file.write_text(
        setup_project_file.read_text(
            encoding="utf-8",
        ),
        encoding="utf-8",
    )

    setup_project_preparer.prepare.return_value = (
        prepared_setup_file
    )

    #
    # Setup Workspace Service
    #

    # O projeto original nunca é substituído.
    # O workspace temporário é utilizado somente
    # para preparação e limpeza.
    #

    setup_workspace_service = MagicMock(
        spec=SetupWorkspaceService,
    )

    #
    # Process Service
    #

    # O processo externo NÃO será executado.
    #
    # O mock simula:
    #
    # 1. execução bem-sucedida do Visual Studio;
    # 2. criação do MSI intermediário.
    #

    process_service = MagicMock()

    def execute_process(
        command,
    ):
        """
        Simula a execução do Visual Studio
        e a criação do MSI intermediário.
        """

        intermediate_msi = (
            prepared_setup_file.parent
            / "Release"
            / "Teste.msi"
        )

        intermediate_msi.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        intermediate_msi.write_bytes(
            b"MSI_TESTE",
        )

        return MagicMock(
            status=ProcessStatus.SUCCESS,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

    process_service.execute.side_effect = (
        execute_process
    )

    #
    # Disable Out Of Proc Build
    #

    # O teste não executa o utilitário real.
    # Simulamos uma execução bem-sucedida.
    #

    disable_out_of_proc_build_service = MagicMock(
        spec=DisableOutOfProcBuildService,
    )

    disable_out_of_proc_build_service.execute.return_value = (
        MagicMock(
            status=ProcessStatus.SUCCESS,
            exit_code=0,
            stdout="Success.",
            stderr="",
            duration=0.1,
        )
    )

    #
    # Visual Studio Locator
    #

    visual_studio_locator = MagicMock()

    visual_studio_locator.locate.return_value = (
        Path(
            r"C:\Program Files"
            r"\Microsoft Visual Studio"
            r"\2022\Professional"
            r"\Common7\IDE"
            r"\devenv.com"
        )
    )

    #
    # Visual Studio Installer
    #

    installer = (
        VisualStudioInstallerService(
            process_service=process_service,
            visual_studio_locator=(
                visual_studio_locator
            ),
            disable_out_of_proc_build_service=(
                disable_out_of_proc_build_service
            ),
        )
    )

    #
    # Advanced Installer
    #

    # O teste está validando especificamente
    # o fluxo do Visual Studio.
    #
    # Portanto não executamos o Advanced Installer.
    # Apenas fornecemos um InstallerService
    # simulado para satisfazer o contrato da Factory.
    #

    advanced_installer = MagicMock(
        spec=InstallerService,
    )

    #
    # Factory
    #

    setup_factory = (
        DefaultSetupFactory(
            visual_studio_installer=(
                installer
            ),
            advanced_installer=(
                advanced_installer
            ),
        )
    )

    #
    # Settings
    #

    settings = MagicMock()

    settings.setup_output_path = (
        setup_output_path
    )

    settings.setup.engine = (
        SetupEngine.VISUAL_STUDIO
    )

    #
    # Orchestrator
    #

    orchestrator = (
        DefaultSetupOrchestrator(
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
            settings=settings,
        )
    )

    #
    # Execução
    #

    result = orchestrator.execute(
        request,
    )

    #
    # Validações
    #

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )

    assert result.output_msi.exists()

    assert result.output_msi.read_bytes() == (
        b"MSI_TESTE"
    )

    #
    # Confirma que o workspace foi criado
    # fora de C:\Setups.
    #

    setup_project_preparer.prepare.assert_called_once()

    setup_workspace_service.backup_original.assert_not_called()

    setup_workspace_service.replace_original.assert_not_called()

    setup_workspace_service.restore_original.assert_not_called()

    setup_workspace_service.cleanup.assert_called_once()

    #
    # Confirma execução do processo.
    #

    process_service.execute.assert_called_once()

    visual_studio_locator.locate.assert_called_once()

    #
    # Confirma que o DisableOutOfProcBuild
    # foi executado antes do Visual Studio.
    #

    disable_out_of_proc_build_service.execute.assert_called_once_with(
        visual_studio_path=(
            visual_studio_locator.locate.return_value
        )
    )