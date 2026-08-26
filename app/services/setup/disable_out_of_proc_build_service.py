"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : disable_out_of_proc_build_service.py
Descrição : Desabilita o processamento Out-of-Process do MSBuild
             utilizado pelo Visual Studio.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.models.process.process_result import (
    ProcessResult,
)


class DisableOutOfProcBuildService:
    """
    Executa o utilitário DisableOutOfProcBuild.exe
    pertencente à instalação do Visual Studio.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ):
        self.__process_service = (
            process_service
        )

    def execute(
        self,
        visual_studio_path: Path,
    ) -> ProcessResult:
        """
        Desabilita o Out-of-Process Build da
        instalação do Visual Studio informada.
        """

        if not visual_studio_path.exists():
            raise FileNotFoundError(
                "Executável do Visual Studio "
                "não foi encontrado."
            )

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
                "Executável "
                "'DisableOutOfProcBuild.exe' "
                "não foi encontrado."
            )

        command = Command(
            executable=(
                disable_out_of_proc_build
            ),
            working_directory=(
                visual_studio_path.parent
            ),
            arguments=[],
        )

        return self.__process_service.execute(
            command,
        )