"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : disable_out_of_proc_build_service.py
Descrição : Executa o utilitário DisableOutOfProcBuild do Visual Studio.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.command import (
    Command,
)

from app.models.process.process_result import (
    ProcessResult,
)


class DisableOutOfProcBuildService:
    """
    Executa o utilitário DisableOutOfProcBuild.exe
    disponibilizado pelo Visual Studio.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if process_service is None:

            raise ValueError(
                "ProcessService não foi informado."
            )

        self.__process_service = (
            process_service
        )

    def execute(
        self,
        visual_studio_path: Path,
    ) -> ProcessResult:
        """
        Executa o DisableOutOfProcBuild.exe
        associado à instalação do Visual Studio.
        """

        if visual_studio_path is None:

            raise ValueError(
                "Executável do Visual Studio "
                "não foi informado."
            )

        visual_studio_path = Path(
            visual_studio_path,
        )

        #
        # ------------------------------------------------------------
        # Validação do executável do Visual Studio.
        # ------------------------------------------------------------
        #

        if not visual_studio_path.exists():

            raise FileNotFoundError(
                "Executável do Visual Studio "
                "não encontrado: "
                f"{visual_studio_path}"
            )

        if not visual_studio_path.is_file():

            raise ValueError(
                "Executável do Visual Studio "
                "não é um arquivo: "
                f"{visual_studio_path}"
            )

        #
        # ------------------------------------------------------------
        # Localização do DisableOutOfProcBuild.
        # ------------------------------------------------------------
        #

        disable_out_of_proc_build = (
            visual_studio_path.parent
            / "CommonExtensions"
            / "Microsoft"
            / "VSI"
            / "DisableOutOfProcBuild"
            / "DisableOutOfProcBuild.exe"
        )

        if not disable_out_of_proc_build.exists():

            raise FileNotFoundError(
                "DisableOutOfProcBuild.exe "
                "não encontrado: "
                f"{disable_out_of_proc_build}"
            )

        if not disable_out_of_proc_build.is_file():

            raise ValueError(
                "DisableOutOfProcBuild.exe "
                "não é um arquivo: "
                f"{disable_out_of_proc_build}"
            )

        #
        # ------------------------------------------------------------
        # Criação do comando.
        # ------------------------------------------------------------
        #

        command = Command(
            executable=(
                disable_out_of_proc_build
            ),
            working_directory=(
                visual_studio_path.parent
            ),
            arguments=[],
        )

        #
        # ------------------------------------------------------------
        # Execução.
        # ------------------------------------------------------------
        #

        return (
            self.__process_service.execute(
                command,
            )
        )