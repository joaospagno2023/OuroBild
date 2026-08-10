"""
---------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_step.py
Descrição: Executa a etapa de compilação da Pipeline.
---------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)
from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.process.command_argument import (
    CommandArgument,
)
from app.parsers.msbuild.msbuild_parser import (
    MsBuildParser,
)
from app.pipeline.steps.process_step import (
    ProcessStep,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)
from app.utils.pipeline_logger import (
    PipelineLogger,
)


class BuildStep(ProcessStep):
    """
    Executa a etapa de compilação.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Build"

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

        self.__msbuild_locator = (
            msbuild_locator
        )

    def __normalize_platform(
        self,
        platform: str,
    ) -> str:
        """
        Normaliza o nome da plataforma para o formato
        esperado pelo MSBuild.
        """

        if not platform:
            return platform

        normalized = (
            platform.strip()
            .replace(" ", "")
        )

        aliases = {

            "ANYCPU": "AnyCPU",

            "X64": "x64",

            "X86": "x86",

            "WIN32": "Win32",

            "MIXEDPLATFORMS": "Mixed Platforms",
        }

        return aliases.get(
            normalized.upper(),
            normalized,
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o executável responsável pela compilação.
        """

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        #
        # Compilação utilizando MSBuild.
        #

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):

            return (
                self.__msbuild_locator.get_msbuild_path()
            )

        #
        # Compilação utilizando o SDK do .NET.
        #

        return Path(
            "dotnet",
        )

    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:

        build_context = (
            context.variables["build_context"]
        )

        return (
            build_context.paths.project_file.parent
        )

    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        #
        # MSBuild
        #

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):

            platform = (
                self.__normalize_platform(
                    project.platform,
                )
            )

            #
            # DEBUG MSBUILD
            #

            PipelineLogger.info(
                "MSBUILD CONFIGURATION",
            )

            PipelineLogger.info(
                f"Project........: "
                f"{project.name}",
            )

            PipelineLogger.info(
                f"Project File...: "
                f"{build_context.paths.project_file}",
            )

            PipelineLogger.info(
                f"Configuration..: "
                f"{project.configuration}",
            )

            PipelineLogger.info(
                f"Platform.......: "
                f"{project.platform}",
            )

            PipelineLogger.info(
                f"Normalized.....: "
                f"{platform}",
            )

            PipelineLogger.info(
                f"MSBuild........: "
                f"{self.__msbuild_locator.get_msbuild_path()}",
            )

            #
            # ARGUMENTOS MSBUILD
            #

            PipelineLogger.info(
                "MSBUILD ARGUMENTS",
            )

            PipelineLogger.info(
                f"Project........: "
                f"{build_context.paths.project_file}",
            )

            PipelineLogger.info(
                f"Configuration..: "
                f"/p:Configuration="
                f"{project.configuration}",
            )

            PipelineLogger.info(
                f"Platform.......: "
                f"/p:Platform="
                f"{platform}",
            )

            #
            # Retorna argumentos
            #

            return [

                CommandArgument(
                    value=str(
                        build_context.paths.project_file
                    ),
                ),

                CommandArgument(
                    value=(
                        f"/p:Configuration="
                        f"{project.configuration}"
                    ),
                ),

                CommandArgument(
                    value=(
                        f"/p:Platform="
                        f"{platform}"
                    ),
                ),
            ]

        #
        # DotNet CLI
        #

        return [

            CommandArgument(
                value="build",
            ),

            CommandArgument(
                value=str(
                    build_context.paths.project_file
                ),
            ),

            CommandArgument(
                value="--configuration",
            ),

            CommandArgument(
                value=project.configuration,
            ),

            CommandArgument(
                value="--no-restore",
            ),
        ]

    def get_output_parser(
        self,
    ):
        """
        Retorna o parser responsável por interpretar
        a saída do processo de Build.
        """

        return MsBuildParser()