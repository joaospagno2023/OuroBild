"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_installer_service.py
Descrição : Gera o Setup utilizando o projeto de instalação
            do Visual Studio (.vdproj).
--------------------------------------------------------------------
"""

import shutil

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

from app.services.setup.disable_out_of_proc_build_service import (
    DisableOutOfProcBuildService,
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
        disable_out_of_proc_build_service: (
            DisableOutOfProcBuildService
        ),
    ) -> None:
        """
        Inicializa o serviço.
        """

        if process_service is None:
            raise ValueError(
                "O serviço de processos "
                "não foi informado."
            )

        if visual_studio_locator is None:
            raise ValueError(
                "O localizador do Visual Studio "
                "não foi informado."
            )

        if disable_out_of_proc_build_service is None:
            raise ValueError(
                "O serviço DisableOutOfProcBuild "
                "não foi informado."
            )

        self.__process_service = (
            process_service
        )

        self.__visual_studio_locator = (
            visual_studio_locator
        )

        self.__disable_out_of_proc_build_service = (
            disable_out_of_proc_build_service
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

        disable_result = (
            self.__disable_out_of_proc_build_service
            .execute(
                visual_studio_path,
            )
        )

        if (
            disable_result.status
            != ProcessStatus.SUCCESS
        ):
            return SetupResult(
                success=False,
                message=(
                    "Falha ao desabilitar o "
                    "Out-of-Proc Build do Visual Studio. "
                    f"ExitCode: "
                    f"{disable_result.exit_code}. "
                    f"{disable_result.stderr}"
                ).strip(),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    disable_result.duration
                ),
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

        intermediate_msi = (
            self.__get_intermediate_msi_path(
                definition=definition,
            )
        )

        if not intermediate_msi.exists():
            return SetupResult(
                success=False,
                message=(
                    "MSI intermediário "
                    "não foi encontrado: "
                    f"{intermediate_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        output_msi = Path(
            paths.output_msi,
        )

        output_msi.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            intermediate_msi,
            output_msi,
        )
        intermediate_msi.unlink()
        
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

    @staticmethod
    def __get_intermediate_msi_path(
        definition: SetupDefinition,
    ) -> Path:
        """
        Obtém o caminho do MSI intermediário gerado
        pelo Visual Studio.

        Estrutura:

            <SetupProject>
                <Configuration>
                    <SetupProject>.msi
        """

        return (
            definition.setup_project_path.parent
            / definition.configuration
            / (
                definition.setup_project_path.stem
                + ".msi"
            )
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

        if self.__process_service is None:
            raise ValueError(
                "O serviço de processos "
                "não foi informado."
            )

        if self.__visual_studio_locator is None:
            raise ValueError(
                "O localizador do Visual Studio "
                "não foi informado."
            )

        if (
            self.__disable_out_of_proc_build_service
            is None
        ):
            raise ValueError(
                "O serviço DisableOutOfProcBuild "
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

        log_path = (
            definition.solution_path.parent
            / "OuroBuild.devenv.log.xml"
        )

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
                value=definition.setup_project_path.stem,
            ),

            CommandArgument(
                value="/ProjectConfig",
            ),

            CommandArgument(
                value=definition.configuration,
            ),

            CommandArgument(
                value="/Log",
            ),

            CommandArgument(
                value=str(
                    log_path,
                ),
            ),
        ]

        return Command(
            executable=visual_studio_path,
            working_directory=(
                definition.solution_path.parent
            ),
            arguments=arguments,
        )