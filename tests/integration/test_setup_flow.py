"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_flow.py
Descrição : Teste de integração do fluxo de geração de Setup.
--------------------------------------------------------------------
"""

from pathlib import Path
from unittest.mock import MagicMock

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

from app.services.setup.visual_studio_installer_service import (
    VisualStudioInstallerService,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)

from app.services.setup.visual_studio_setup_preparer import (
    VisualStudioSetupPreparer,
)

from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)


def create_solution(
    solution_path: Path,
    project_path: Path,
) -> None:
    """
    Cria uma Solution mínima para o teste.

    O conteúdo é suficiente para representar
    uma Solution contendo o projeto informado.
    """

    project_guid = (
        "11111111-1111-1111-1111-111111111111"
    )

    solution_content = (
        "Microsoft Visual Studio Solution File, "
        "Format Version 12.00\n"
        "# Visual Studio Version 17\n"
        "VisualStudioVersion = 17.0.31903.59\n"
        "MinimumVisualStudioVersion = 10.0.40219.1\n"
        f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = '
        f'"Projeto", "{project_path.name}", '
        f'"{{{project_guid}}}"\n'
        "EndProject\n"
        "Global\n"
        "\tGlobalSection(SolutionConfigurationPlatforms) = "
        "preSolution\n"
        "\t\tDebug|Any CPU = Debug|Any CPU\n"
        "\t\tRelease|Any CPU = Release|Any CPU\n"
        "\tEndGlobalSection\n"
        "EndGlobal\n"
    )

    solution_path.write_text(
        solution_content,
        encoding="utf-8",
    )


def create_project_file(
    project_path: Path,
) -> None:
    """
    Cria um projeto .csproj mínimo.
    """

    project_content = """
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
""".strip()

    project_path.write_text(
        project_content,
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
    # O teste não deve executar a preparação real
    # do .vdproj.
    #
    # Aqui simulamos somente o resultado esperado:
    # uma cópia preparada do projeto Setup.
    #

    setup_project_preparer = MagicMock(
        spec=SetupProjectPreparer,
    )

    setup_project_preparer.prepare.return_value = (
        setup_project_file
    )

    #
    # Visual Studio Setup Preparer
    #
    # O teste não deve criar uma Solution real.
    #
    # Simulamos apenas o resultado esperado:
    # uma Solution preparada.
    #

    visual_studio_setup_preparer = MagicMock(
        spec=VisualStudioSetupPreparer,
    )

    prepared_solution_file = (
    setup_output_path
    / ".workspace"
    / "Projeto.sln"
    )

    prepared_solution_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    prepared_solution_file.write_text(
        solution_file.read_text(
            encoding="utf-8",
        ),
        encoding="utf-8",
    )

    visual_studio_setup_preparer.prepare.return_value = (
        prepared_solution_file
    )

    #
    # Process Service
    #
    # O processo externo NÃO será executado.
    #
    # Quando o Orchestrator chegar ao Installer,
    # o mock simulará:
    #
    # 1. execução bem-sucedida do Visual Studio;
    # 2. criação do MSI.
    #

    process_service = MagicMock()

    def execute_process(
        command,
    ):
        """
        Simula a execução do Visual Studio
        e a criação do MSI.
        """

        paths.output_msi.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.output_msi.write_bytes(
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
    # Installer
    #

    installer = (
        VisualStudioInstallerService(
            process_service=process_service,
            visual_studio_locator=(
                visual_studio_locator
            ),
        )
    )

    #
    # Factory
    #

    setup_factory = (
        DefaultSetupFactory(
            visual_studio_installer=(
                installer
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
            visual_studio_setup_preparer=(
                visual_studio_setup_preparer
            ),
            settings=settings,
        )
    )

    #
    # Use Case
    #

    use_case = (
        DefaultExecuteSetupUseCase(
            setup_orchestrator=(
                orchestrator
            ),
        )
    )

    #
    # Execute
    #

    result = use_case.execute(
        request,
    )

    #
    # Assertions
    #

    assert result.success is True

    assert result.project_id == (
        "teste"
    )

    assert result.output_msi == (
        paths.output_msi
    )

    assert result.duration_seconds == (
        1.0
    )

    assert (
        result.message
        == "Setup gerado com sucesso."
    )

    assert paths.output_msi.exists()

    assert (
        paths.output_msi.read_bytes()
        == b"MSI_TESTE"
    )

    #
    # Verificações do fluxo
    #

    workspace_resolver.resolve.assert_called_once()

    setup_path_resolver.resolve.assert_called_once()

    solution_locator.find_solution.assert_called_once()

    definition_loader.load.assert_called_once()

    setup_project_preparer.prepare.assert_called_once()

    visual_studio_setup_preparer.prepare.assert_called_once()

    visual_studio_locator.locate.assert_called_once()

    process_service.execute.assert_called_once()

    #
    # Verifica a preparação da Solution.
    #

    visual_studio_setup_preparer.prepare.assert_called_once_with(
        solution_path=solution_file,
        original_setup_project_path=(
            setup_project_file
        ),
        prepared_setup_project_path=(
            setup_project_file
        ),
        workspace_root=(
            setup_output_path
            / ".workspace"
        ),
    )

    #
    # Comando executado
    #

    command = (
        process_service
        .execute
        .call_args.args[0]
    )

    assert command.executable == (
        visual_studio_locator.locate.return_value
    )

    #
    # O Installer deve utilizar a
    # Solution preparada.
    #

    assert (
        str(prepared_solution_file)
        in [
            argument.value
            for argument in command.arguments
        ]
    )

    assert (
        "/Build"
        in [
            argument.value
            for argument in command.arguments
        ]
    )

    assert (
        "/Project"
        in [
            argument.value
            for argument in command.arguments
        ]
    )

    assert (
        setup_project_file.stem
        in [
            argument.value
            for argument in command.arguments
        ]
    )