"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_installer_service.py
Descrição : Gera o Setup utilizando o projeto de instalação
            do Visual Studio (.vdproj).
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.installer_service import (
    InstallerService,
)

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.models.process.process_status import (
    ProcessStatus,
)

from app.models.setup.setup_definition import (
    SetupDefinition,
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

from app.services.setup.visual_studio_locator import (
    VisualStudioLocator,
)


class VisualStudioInstallerService(
    InstallerService,
):
    """
    Gera um instalador utilizando um projeto
    Visual Studio Installer (.vdproj).
    """

    def __init__(
        self,
        process_service: ProcessService,
        visual_studio_locator: VisualStudioLocator,
    ) -> None:
        """
        Inicializa o serviço.

        Args:
            process_service:
                Serviço responsável pela execução
                de processos externos.

            visual_studio_locator:
                Serviço responsável por localizar
                o Visual Studio instalado.
        """

        self.__process_service = (
            process_service
        )

        self.__visual_studio_locator = (
            visual_studio_locator
        )

    def install(
        self,
        request: SetupRequest,
        definition: SetupDefinition,
        paths: SetupPaths,
    ) -> SetupResult:
        """
        Gera o instalador utilizando o Visual Studio.
        """

        self.__validate(
            request=request,
            definition=definition,
            paths=paths,
        )

        visual_studio_path = (
            self.__visual_studio_locator.locate()
        )

        command = self.__create_command(
            definition=definition,
            visual_studio_path=visual_studio_path,
        )

        process_result = (
            self.__process_service.execute(
                command,
            )
        )

        if (
            process_result.status
            != ProcessStatus.SUCCESS
        ):
            return SetupResult(
                success=False,
                message=(
                    "Falha ao gerar o Setup "
                    "utilizando o Visual Studio. "
                    f"ExitCode: "
                    f"{process_result.exit_code}. "
                    f"{process_result.stderr}"
                ).strip(),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        output_msi = Path(
            paths.output_msi,
        )

        if not output_msi.exists():
            return SetupResult(
                success=False,
                message=(
                    "O Visual Studio finalizou "
                    "a geração do Setup, porém "
                    "o arquivo MSI não foi encontrado: "
                    f"{output_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        return SetupResult(
            success=True,
            message=(
                "Setup gerado com sucesso."
            ),
            project_id=request.project_id,
            output_msi=output_msi,
            duration_seconds=(
                process_result.duration
            ),
        )

    def __validate(
        self,
        request: SetupRequest,
        definition: SetupDefinition,
        paths: SetupPaths,
    ) -> None:
        """
        Valida os dados necessários para geração.
        """

        if request is None:
            raise ValueError(
                "A solicitação de Setup "
                "não foi informada."
            )

        if definition is None:
            raise ValueError(
                "A definição do Setup "
                "não foi informada."
            )

        if paths is None:
            raise ValueError(
                "Os caminhos do Setup "
                "não foram informados."
            )

        if self.__visual_studio_locator is None:
            raise ValueError(
                "O localizador do Visual Studio "
                "não foi informado."
            )

        if not definition.solution_path.exists():
            raise FileNotFoundError(
                "A solução do Setup "
                "não foi encontrada: "
                f"{definition.solution_path}"
            )

        if not definition.setup_project_path.exists():
            raise FileNotFoundError(
                "O projeto de Setup "
                "não foi encontrado: "
                f"{definition.setup_project_path}"
            )

    def __create_command(
        self,
        definition: SetupDefinition,
        visual_studio_path: Path,
    ) -> Command:
        """
        Cria o comando do Visual Studio.
        """

        arguments = [
            CommandArgument(
                value=str(
                    definition.solution_path,
                ),
            ),

            CommandArgument(
                value="/Build",
            ),

            CommandArgument(
                value=definition.configuration,
            ),

            CommandArgument(
                value="/Project",
            ),

            CommandArgument(
                value=str(
                    definition.setup_project_path,
                ),
            ),

            CommandArgument(
                value="/ProjectConfig",
            ),

            CommandArgument(
                value=definition.configuration,
            ),
        ]

        return Command(
            executable=visual_studio_path,
            working_directory=(
                definition.solution_path.parent
            ),
            arguments=arguments,
        )