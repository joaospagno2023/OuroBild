"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : restore_step.py
Descrição : Etapa responsável pela execução do Restore.
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
from app.models.pipeline.step_result import (
    StepResult,
)
from app.models.pipeline.step_status import (
    StepStatus,
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
from app.services.project_metadata_service import (
    ProjectMetadataService,
)


class RestoreStep(ProcessStep):
    """
    Executa o Restore do projeto.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Restore"

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
        project_metadata_service: ProjectMetadataService,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

        self.__msbuild_locator = (
            msbuild_locator
        )

        self.__project_metadata_service = (
            project_metadata_service
        )

    def should_execute(
        self,
        context: PipelineContext,
    ) -> bool:
        """
        Verifica se o Restore precisa ser executado.

        O Restore será executado quando:

        - não existir metadata;
        - não existir restore_hash;
        - o hash atual do projeto for diferente
          do hash registrado no último Restore.

        Quando o hash for igual, a Step será marcada
        como SKIPPED pelo ProcessStep.
        """

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        project_file = (
            build_context.paths.project_file
        )

        return (
            self.__project_metadata_service
            .is_restore_required(
                project_id=project.id,
                project_file=project_file,
            )
        )

    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa o Restore.

        O restore_hash somente é atualizado quando
        o Restore termina com sucesso.
        """

        result = super().execute(
            context,
        )

        #
        # SKIPPED
        #
        # Se o Restore não era necessário, não
        # devemos alterar a metadata.
        #

        if result.status == StepStatus.SKIPPED:

            return result

        #
        # FAILED
        #
        # Se o Restore falhou, não atualizamos
        # o restore_hash.
        #

        if result.status != StepStatus.SUCCESS:

            return result

        #
        # SUCCESS
        #
        # Somente agora registramos o hash do
        # projeto como restaurado.
        #

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        project_file = (
            build_context.paths.project_file
        )

        self.__project_metadata_service.update_restore_hash(
            project_id=project.id,
            project_file=project_file,
        )

        return result

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o executável utilizado pelo Restore.
        """

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

        return Path("dotnet")

    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o diretório de trabalho do Restore.
        """

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
        """
        Retorna os argumentos utilizados pelo Restore.
        """

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

            restore_target = (
                build_context.paths.solution_file
                or build_context.paths.project_file
            )

            return [
                CommandArgument(
                    value=str(
                        restore_target,
                    ),
                ),
                CommandArgument(
                    value="/t:Restore",
                ),
            ]

        #
        # DotNet
        #

        return [
            CommandArgument(
                value="restore",
            ),
            CommandArgument(
                value=str(
                    build_context.paths.project_file,
                ),
            ),
        ]