"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_pipeline_use_case.py
Descrição : Responsável por executar uma Pipeline de Build.
--------------------------------------------------------------------
"""

from pathlib import Path
from typing import Callable

from app.abstractions.pipeline_factory import (
    PipelineFactory,
)

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)

from app.factories.build_context_factory import (
    BuildContextFactory,
)

from app.factories.build_environment_builder_factory import (
    BuildEnvironmentBuilderFactory,
)

from app.factories.publish_context_factory import (
    PublishContextFactory,
)

from app.models.build.build_context import (
    BuildContext,
)

from app.models.build.build_request import (
    BuildRequest,
)

from app.models.execution.pipeline_execution_state import (
    PipelineExecutionPhase,
)

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)

from app.models.pipeline.pipeline_result import (
    PipelineResult,
)

from app.models.publish.publish_request import (
    PublishRequest,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.pipeline.runner.pipeline_runner import (
    PipelineRunner,
)

from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)

from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)

from app.utils.pipeline_logger import (
    PipelineLogger,
)


class ExecutePipelineUseCase:
    """
    Responsável por executar uma Pipeline.

    O fluxo executado é:

    1. Cria o BuildContext.
    2. Resolve os caminhos do Build.
    3. Cria o PublishContext.
    4. Resolve os caminhos do Publish.
    5. Cria o PipelineContext.
    6. Executa a Pipeline.
    7. Gera o Setup quando solicitado.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        pipeline_factory: PipelineFactory,
        build_context_factory: BuildContextFactory,
        publish_context_factory: PublishContextFactory,
        solution_locator: SolutionLocatorService,
        pipeline_runner: PipelineRunner,
        execute_setup_use_case: (
            DefaultExecuteSetupUseCase | None
        ) = None,
        pipeline_execution_repository: (
            PipelineExecutionRepository | None
        ) = None,
    ) -> None:
        """
        Inicializa o caso de uso.
        """

        self.__project_repository = (
            project_repository
        )

        self.__pipeline_factory = (
            pipeline_factory
        )

        self.__build_context_factory = (
            build_context_factory
        )

        self.__publish_context_factory = (
            publish_context_factory
        )

        self.__pipeline_runner = (
            pipeline_runner
        )

        self.__execute_setup_use_case = (
            execute_setup_use_case
        )

        self.__pipeline_execution_repository = (
            pipeline_execution_repository
        )

        self.__builder_factory = (
            BuildEnvironmentBuilderFactory(
                solution_locator=solution_locator,
            )
        )

    def execute(
        self,
        project_id: str,
        environment_id: str | None = None,
        version: str | None = None,
        revision: int | None = None,
        publication_mode: str | None = None,
        progress_callback: Callable[
            [
                str,
                int,
                int,
                int,
                PipelineExecutionPhase,
            ],
            None,
        ] | None = None,
        execution_id: str | None = None,
    ) -> PipelineResult:
        """
        Executa a Pipeline e, quando solicitado,
        gera o Setup.

        publication_mode é recebido pela camada de execução para manter
        compatibilidade com o fluxo de publicação. A publicação em rede
        ocorre posteriormente pelo PublishSetupsUseCase.
        """

        build_request = BuildRequest(
            project_id=project_id,
            environment_id=environment_id or "",
            version=version,
            revision=revision,
        )

        #
        # Cria o BuildContext.
        #

        build_context = (
            self.__build_context_factory.create(
                build_request,
            )
        )

        #
        # Resolve os caminhos do Build.
        #

        build_builder = (
            self.__builder_factory.create(
                build_context.environment,
            )
        )

        build_builder.build(
            build_context,
        )

        #
        # Valida o arquivo físico do projeto antes de qualquer etapa
        # de Publish, Build ou execução do Pipeline.
        #
        self.__validate_project_file(
            build_context,
        )

        #
        # Cria o PublishRequest.
        #
        # O BuildRequest não possui as opções
        # específicas de Publish.
        #
        # A versão e a revisão pertencem à execução
        # atual e precisam ser propagadas para o Publish.
        #

        publish_request = PublishRequest(
            project_id=(
                build_context.project.id
            ),
            environment_id=(
                build_context.environment.id
            ),
            version=version,
            revision=revision,
            publish_profile=(
                build_context.project.publish_profile
            ),
        )

        #
        # Cria o PublishContext.
        #

        publish_context = (
            self.__publish_context_factory.create(
                publish_request,
            )
        )

        #
        # Resolve os caminhos do Publish.
        #

        publish_builder = (
            self.__builder_factory.create(
                publish_context.environment,
            )
        )

        publish_builder.build(
            publish_context,
        )

        #
        # Cria o PipelineContext.
        #

        context = PipelineContext()

        context.variables["project"] = (
            build_context.project
        )

        context.variables["project_id"] = (
            build_context.project.id
        )

        context.variables["request"] = (
            build_context.request
        )

        context.variables["environment"] = (
            build_context.environment
        )

        context.variables["paths"] = (
            build_context.paths
        )

        context.variables["build_context"] = (
            build_context
        )

        #
        # O PublishStep e o PublishCommandFactory
        # dependem desta variável.
        #

        context.variables["publish_context"] = (
            publish_context
        )

        #
        # Contexto genérico de execução.
        #

        context.variables["execution_context"] = (
            build_context
        )

        #
        # Cria a Pipeline.
        #

        pipeline = self.__pipeline_factory.create(
            build_context.project,
        )

        #
        # Define o total de etapas da execução.
        #
        # Quando o Setup fizer parte da execução, ele é tratado como
        # uma etapa adicional do fluxo. O total permanece fixo durante
        # toda a execução; apenas o índice e o percentual avançam.
        #

        pipeline_total_steps = len(
            pipeline.steps,
        )

        setup_enabled = (
            self.__execute_setup_use_case is not None
            and environment_id is not None
        )

        setup_total_steps = (
            self.__execute_setup_use_case.get_progress_total_steps(
                SetupRequest(
                    project_id=project_id,
                    environment_id=environment_id or "",
                    version=version,
                    revision=revision,
                    run_build=False,
                )
            )
            if setup_enabled
            else 0
        )

        execution_total_steps = (
            pipeline_total_steps + setup_total_steps
            if setup_enabled
            else pipeline_total_steps
        )

        def pipeline_progress_callback(
            current_step: str,
            current_step_index: int,
            total_steps: int,
            progress_percent: int,
            phase: PipelineExecutionPhase,
        ) -> None:
            if progress_callback is None:
                return

            if execution_total_steps <= 0:
                progress_callback(
                    current_step,
                    current_step_index,
                    execution_total_steps,
                    0,
                    phase,
                )
                return

            overall_progress = int(
                (
                    current_step_index
                    / execution_total_steps
                )
                * 100
            )

            progress_callback(
                current_step,
                current_step_index,
                execution_total_steps,
                min(overall_progress, 100),
                phase,
            )

        #
        # Executa a Pipeline.
        #

        result = self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=context,
            execution_id=execution_id or "",
            project_id=project_id,
            progress_callback=(
                pipeline_progress_callback
                if progress_callback is not None
                else None
            ),
        )

        #
        # Registra a versão solicitada nesta execução.
        # A versão pertence à execução completa e deve ser preservada
        # mesmo quando o Setup não for executado.
        #

        result.version = version

        if self.__pipeline_execution_repository is not None:
            self.__pipeline_execution_repository.save(
                result,
            )

        #
        # Se o Build/Publish falhar, não gera Setup.
        #

        if (
            not result.success
            or self.__execute_setup_use_case is None
            or environment_id is None
        ):
            return result

        #
        # Cria a solicitação de Setup.
        #

        setup_request = SetupRequest(
            project_id=project_id,
            environment_id=environment_id,
            version=version,
            revision=revision,
            run_build=False,
        )

        #
        # Informa que a execução entrou na fase de Setup.
        #
        # O total de etapas permanece fixo durante toda a execução.
        # O Setup informa suas etapas internas e este caso de uso
        # converte os índices locais para o índice global da execução.
        #

        def setup_progress_callback(
            current_step: str,
            current_step_index: int,
            total_steps: int,
            progress_percent: int,
            phase: PipelineExecutionPhase,
        ) -> None:
            if progress_callback is None:
                return

            global_step_index = (
                pipeline_total_steps
                + current_step_index
            )

            if execution_total_steps <= 0:
                overall_progress = 0

            elif current_step_index >= total_steps:
                overall_progress = int(
                    (
                        global_step_index
                        / execution_total_steps
                    )
                    * 100
                )

            else:
                overall_progress = int(
                    (
                        (global_step_index - 1)
                        / execution_total_steps
                    )
                    * 100
                )

            progress_callback(
                current_step,
                global_step_index,
                execution_total_steps,
                min(overall_progress, 100),
                phase,
            )

        #
        # Executa o Setup.
        #

        setup_result = (
            self.__execute_setup_use_case.execute(
                setup_request,
                progress_callback=(
                    setup_progress_callback
                    if progress_callback is not None
                    else None
                ),
            )
        )

        result.steps.extend(
            setup_result.steps,
        )

        #
        # Propaga falha do Setup antes de persistir a execução.
        #
        if not setup_result.success:
            result.success = False
            result.failed_step = "Setup"
            result.message = setup_result.message

            if self.__pipeline_execution_repository is not None:
                self.__pipeline_execution_repository.save(
                    result,
                )

            return result

        #
        # Adiciona o MSI aos artefatos antes de persistir a execução.
        #
        if setup_result.output_msi:
            result.artifacts.append(
                setup_result.output_msi,
            )

        if self.__pipeline_execution_repository is not None:
            self.__pipeline_execution_repository.save(
                result,
            )

        if progress_callback is not None and setup_result.success:
            progress_callback(
                "Setup",
                execution_total_steps,
                execution_total_steps,
                100,
                PipelineExecutionPhase.SETUP,
            )

        #
        # A execução foi concluída com sucesso.
        #
        return result

        #
        # Adiciona o MSI aos artefatos.
        #

        if setup_result.output_msi:
            result.artifacts.append(
                setup_result.output_msi,
            )

        return result


    @staticmethod
    def __validate_project_file(
        build_context: BuildContext,
    ) -> None:
        """
        Valida se o arquivo de projeto configurado existe no Workspace.

        A validação ocorre depois que o BuildEnvironmentBuilder resolve o
        caminho físico e antes de qualquer etapa da Pipeline.
        """

        project = build_context.project
        paths = build_context.paths

        project_id = project.id if project is not None else ""
        project_path = (
            project.project_path
            if project is not None
            else ""
        )
        project_file = paths.project_file
        workspace_root = paths.workspace_root

        PipelineLogger.info(
            "VALIDAÇÃO DO PROJETO"
        )
        PipelineLogger.info(
            f"Project ID........: {project_id}"
        )
        PipelineLogger.info(
            f"Project Path......: {project_path}"
        )
        PipelineLogger.info(
            f"Workspace Root....: {workspace_root}"
        )
        PipelineLogger.info(
            f"Project File......: {project_file}"
        )

        if project_file is None:
            message = (
                "Arquivo do projeto não foi resolvido. "
                f"Project ID: '{project_id}'. "
                f"Project Path: '{project_path}'."
            )

            PipelineLogger.error(
                f"VALIDAÇÃO DO PROJETO - FALHA | {message}"
            )

            raise ValueError(message)

        project_file = Path(project_file)

        if not project_file.is_file():
            message = (
                "Arquivo do projeto não encontrado no Workspace. "
                f"Project ID: '{project_id}'. "
                f"Project Path: '{project_path}'. "
                f"Caminho resolvido: '{project_file}'."
            )

            PipelineLogger.error(
                f"VALIDAÇÃO DO PROJETO - FALHA | {message}"
            )

            raise ValueError(message)

        PipelineLogger.info(
            "VALIDAÇÃO DO PROJETO - OK"
        )

