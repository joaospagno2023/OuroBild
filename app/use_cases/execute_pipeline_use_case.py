
"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_pipeline_use_case.py
Descrição : Responsável por executar uma Pipeline de Build.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import (
    PipelineFactory,
)

from app.abstractions.project_repository import (
    ProjectRepository,
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

from app.models.build.build_request import (
    BuildRequest,
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
    ) -> PipelineResult:
        """
        Executa a Pipeline e, quando solicitado,
        gera o Setup.
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
        # Cria o PublishRequest.
        #
        # O BuildRequest não possui as opções
        # específicas de Publish.
        #

        publish_request = PublishRequest(
            project_id=(
                build_context.project.id
            ),
            environment_id=(
                build_context.environment.id
            ),
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
        # Executa a Pipeline.
        #

        result = self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=context,
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
        # Executa o Setup.
        #

        setup_result = (
            self.__execute_setup_use_case.execute(
                setup_request,
            )
        )

        result.steps.extend(
            setup_result.steps,
        )

        #
        # Propaga falha do Setup.
        #

        if not setup_result.success:

            result.success = False

            result.failed_step = "Setup"

            result.message = (
                setup_result.message
            )

            return result

        #
        # Adiciona o MSI aos artefatos.
        #

        if setup_result.output_msi:

            result.artifacts.append(
                setup_result.output_msi,
            )

        return result
