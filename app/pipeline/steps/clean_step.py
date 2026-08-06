"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : clean_step.py
Descrição : Etapa responsável pela limpeza do projeto.
--------------------------------------------------------------------
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
from app.pipeline.steps.process_step import (
    ProcessStep,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


class CleanStep(ProcessStep):
    """
    Executa a limpeza do projeto.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Clean"

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

        if not platform:
            return platform

        normalized = (
            platform.strip()
            .replace(
                " ",
                "",
            )
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

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):

            return (
                self.__msbuild_locator.get_msbuild_path()
            )

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

            return [

                CommandArgument(
                    value=str(
                        build_context.paths.project_file,
                    ),
                ),

                CommandArgument(
                    value="/t:Clean",
                ),

                CommandArgument(
                    value=f"/p:Configuration={project.configuration}",
                ),

                CommandArgument(
                    value=f"/p:Platform={platform}",
                ),
            ]

        #
        # Dotnet
        #

        return [

            CommandArgument(
                value="clean",
            ),

            CommandArgument(
                value=str(
                    build_context.paths.project_file,
                ),
            ),

            CommandArgument(
                value="--configuration",
            ),

            CommandArgument(
                value=project.configuration,
            ),
        ]