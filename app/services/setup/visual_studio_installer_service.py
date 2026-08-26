"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_installer_service.py
Descrição : Gera o Setup utilizando o projeto de instalação
            do Visual Studio (.vdproj).
--------------------------------------------------------------------
"""

from pathlib import Path
import shutil

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

        #
        # Localiza o Visual Studio.
        #

        visual_studio_path = (
            self.__visual_studio_locator.locate()
        )

        print(
            "\n"
            "============================================================\n"
            "[OuroBuild] VISUAL STUDIO\n"
            "============================================================"
        )

        print(
            "[OuroBuild] Executável:"
        )

        print(
            f"[OuroBuild] {visual_studio_path}"
        )

        #
        # Desabilita o Out-of-Process Build.
        #

        print(
            "[OuroBuild] Desabilitando "
            "Out-of-Process Build..."
        )

        disable_result = (
            self.__disable_out_of_proc_build_service.execute(
                visual_studio_path=(
                    visual_studio_path
                ),
            )
        )

        print(
            "[OuroBuild] DisableOutOfProcBuild "
            "Status:"
        )

        print(
            f"[OuroBuild] {disable_result.status}"
        )

        print(
            "[OuroBuild] DisableOutOfProcBuild "
            "ExitCode:"
        )

        print(
            f"[OuroBuild] {disable_result.exit_code}"
        )

        print(
            "[OuroBuild] DisableOutOfProcBuild "
            "STDOUT:"
        )

        print(
            disable_result.stdout
            if disable_result.stdout
            else "<vazio>"
        )

        print(
            "[OuroBuild] DisableOutOfProcBuild "
            "STDERR:"
        )

        print(
            disable_result.stderr
            if disable_result.stderr
            else "<vazio>"
        )

        #
        # O utilitário precisa terminar com sucesso
        # antes de iniciarmos o Visual Studio.
        #

        if (
            disable_result.status
            != ProcessStatus.SUCCESS
        ):
            return SetupResult(
                success=False,
                message=(
                    "Não foi possível desabilitar "
                    "o Out-of-Process Build do "
                    "Visual Studio. "
                    f"ExitCode: "
                    f"{disable_result.exit_code}. "
                    f"STDOUT: "
                    f"{disable_result.stdout}. "
                    f"STDERR: "
                    f"{disable_result.stderr}"
                ).strip(),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    disable_result.duration
                ),
            )

        #
        # Resolve o MSI intermediário.
        #

        intermediate_msi = (
            self.__resolve_intermediate_msi(
                definition=definition,
            )
        )

        print(
            "[OuroBuild] MSI intermediário esperado:"
        )

        print(
            f"[OuroBuild] {intermediate_msi}"
        )

        #
        # Cria o comando.
        #

        command = self.__create_command(
            definition=definition,
            visual_studio_path=visual_studio_path,
        )

        #
        # Mostra todas as informações antes
        # de executar o processo.
        #

        self.__print_command(
            command=command,
            definition=definition,
        )

        #
        # Executa o Visual Studio.
        #

        print(
            "[OuroBuild] Executando Visual Studio..."
        )

        process_result = (
            self.__process_service.execute(
                command,
            )
        )

        #
        # Resultado do processo.
        #

        print(
            "\n"
            "============================================================\n"
            "[OuroBuild] RESULTADO DO VISUAL STUDIO\n"
            "============================================================"
        )

        print(
            "[OuroBuild] Status:"
        )

        print(
            f"[OuroBuild] {process_result.status}"
        )

        print(
            "[OuroBuild] ExitCode:"
        )

        print(
            f"[OuroBuild] {process_result.exit_code}"
        )

        print(
            "[OuroBuild] Duration:"
        )

        print(
            f"[OuroBuild] {process_result.duration}"
        )

        print(
            "[OuroBuild] STDOUT:"
        )

        print(
            process_result.stdout
            if process_result.stdout
            else "<vazio>"
        )

        print(
            "[OuroBuild] STDERR:"
        )

        print(
            process_result.stderr
            if process_result.stderr
            else "<vazio>"
        )

        print(
            "============================================================\n"
        )

        #
        # Visual Studio falhou.
        #

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
                    f"STDOUT: "
                    f"{process_result.stdout}. "
                    f"STDERR: "
                    f"{process_result.stderr}"
                ).strip(),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        #
        # Visual Studio terminou com sucesso.
        #

        print(
            "[OuroBuild] Verificando MSI intermediário:"
        )

        print(
            f"[OuroBuild] {intermediate_msi}"
        )

        if not intermediate_msi.exists():
            return SetupResult(
                success=False,
                message=(
                    "O Visual Studio finalizou "
                    "a geração do Setup, porém "
                    "o MSI intermediário não foi "
                    "encontrado em: "
                    f"{intermediate_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        #
        # Caminho final do MSI.
        #

        output_msi = Path(
            paths.output_msi,
        )

        print(
            "[OuroBuild] MSI final:"
        )

        print(
            f"[OuroBuild] {output_msi}"
        )

        #
        # Garante que a pasta final exista.
        #

        output_msi.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        #
        # Remove MSI anterior.
        #

        if output_msi.exists():

            try:

                output_msi.unlink()

            except OSError as error:

                return SetupResult(
                    success=False,
                    message=(
                        "Não foi possível remover "
                        "o MSI anterior no destino final: "
                        f"{output_msi}. "
                        f"Erro: {error}"
                    ),
                    project_id=request.project_id,
                    output_msi=None,
                    duration_seconds=(
                        process_result.duration
                    ),
                )

        #
        # Copia o MSI gerado pelo Visual Studio.
        #

        try:

            shutil.copy2(
                intermediate_msi,
                output_msi,
            )

        except OSError as error:

            return SetupResult(
                success=False,
                message=(
                    "O MSI foi gerado pelo Visual Studio, "
                    "porém não foi possível copiá-lo "
                    "para o destino final. "
                    f"Origem: {intermediate_msi}. "
                    f"Destino: {output_msi}. "
                    f"Erro: {error}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        #
        # Confirma MSI final.
        #

        if not output_msi.exists():
            return SetupResult(
                success=False,
                message=(
                    "A cópia do MSI foi executada, "
                    "porém o arquivo final não foi "
                    "encontrado: "
                    f"{output_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        #
        # Confirma tamanho.
        #

        if output_msi.stat().st_size <= 0:
            return SetupResult(
                success=False,
                message=(
                    "O MSI final foi criado, "
                    "porém possui tamanho inválido: "
                    f"{output_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    process_result.duration
                ),
            )

        #
        # Remove MSI intermediário somente depois
        # de confirmar a cópia.
        #

        try:

            intermediate_msi.unlink()

        except OSError as error:

            return SetupResult(
                success=True,
                message=(
                    "Setup gerado e copiado com sucesso, "
                    "porém não foi possível remover "
                    "o MSI intermediário. "
                    f"Origem: {intermediate_msi}. "
                    f"Erro: {error}"
                ),
                project_id=request.project_id,
                output_msi=output_msi,
                duration_seconds=(
                    process_result.duration
                ),
            )

        return SetupResult(
            success=True,
            message=(
                "Setup gerado com sucesso. "
                f"MSI final: {output_msi}"
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

    def __resolve_intermediate_msi(
        self,
        definition: SetupDefinition,
    ) -> Path:
        """
        Resolve o caminho onde o Visual Studio
        deverá gerar o MSI intermediário.
        """

        setup_project_path = Path(
            definition.setup_project_path,
        )

        release_path = (
            setup_project_path.parent
            / definition.configuration
        )

        msi_name = (
            f"{setup_project_path.stem}.msi"
        )

        return (
            release_path
            / msi_name
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

    @staticmethod
    def __print_command(
        command: Command,
        definition: SetupDefinition,
    ) -> None:
        """
        Exibe no console o comando completo.
        """

        executable = Path(
            command.executable,
        )

        arguments = []

        for argument in command.arguments:

            value = str(
                argument.value,
            )

            if (
                " " in value
                or "\t" in value
            ):

                value = (
                    '"'
                    + value.replace(
                        '"',
                        '\\"',
                    )
                    + '"'
                )

            arguments.append(
                value
            )

        executable_text = str(
            executable,
        )

        if (
            " " in executable_text
            or "\t" in executable_text
        ):

            executable_text = (
                '"'
                + executable_text
                + '"'
            )

        command_text = (
            executable_text
            + " "
            + " ".join(
                arguments,
            )
        )

        print(
            "\n"
            "============================================================\n"
            "[OuroBuild] COMANDO DO VISUAL STUDIO\n"
            "============================================================"
        )

        print(
            command_text
        )

        print(
            "\n[OuroBuild] WORKING DIRECTORY"
        )

        print(
            command.working_directory
        )

        print(
            "\n[OuroBuild] SOLUTION"
        )

        print(
            definition.solution_path
        )

        print(
            "\n[OuroBuild] SETUP PROJECT"
        )

        print(
            definition.setup_project_path
        )

        print(
            "\n============================================================\n"
        )