"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_build_use_case.py
Descrição : Responsável por iniciar uma execução de Build.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import (
    PipelineFactory,
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
from app.pipeline.runner.pipeline_runner import (
    PipelineRunner,
)
from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)


class ExecuteBuildUseCase:
    """
    Responsável por iniciar uma execução de Build.
    """

    def __init__(
        self,
        build_context_factory: BuildContextFactory,
        publish_context_factory: PublishContextFactory,
        pipeline_factory: PipelineFactory,
        solution_locator: SolutionLocatorService,
        pipeline_runner: PipelineRunner,
    ) -> None:

        self.__build_context_factory = (
            build_context_factory
        )

        self.__publish_context_factory = (
            publish_context_factory
        )

        self.__pipeline_runner = (
            pipeline_runner
        )

        self.__pipeline_factory = (
            pipeline_factory
        )

        self.__builder_factory = (
            BuildEnvironmentBuilderFactory(
                solution_locator=solution_locator,
            )
        )

    def execute(
        self,
        request: BuildRequest,
    ) -> PipelineResult:
        """
        Executa uma Pipeline de Build.
        """

        #
        # Cria o BuildContext
        #

        build_context = (
            self.__build_context_factory.create(
                request,
            )
        )

        #
        # Resolve os caminhos do Build
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
        # Cria o PublishRequest
        #
        # O BuildRequest não possui as opções específicas
        # de Publish. Portanto, usamos somente os dados
        # necessários para identificar o projeto e ambiente.
        #
        # Os demais campos utilizam os valores padrão
        # definidos em PublishRequest.
        #

        publish_request = PublishRequest(
            project_id=(
                build_context.project.id
            ),
            environment_id=(
                build_context.environment.id
            ),
        )

        #
        # Cria o PublishContext
        #

        publish_context = (
            self.__publish_context_factory.create(
                publish_request,
            )
        )

        #
        # Resolve os caminhos do Publish
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
        # Cria o PipelineContext
        #

        pipeline_context = PipelineContext()

        pipeline_context.variables["project"] = (
            build_context.project
        )

        pipeline_context.variables["project_id"] = (
            build_context.project.id
        )

        pipeline_context.variables["request"] = (
            build_context.request
        )

        pipeline_context.variables["environment"] = (
            build_context.environment
        )

        pipeline_context.variables["paths"] = (
            build_context.paths
        )

        #
        # Compatibilidade com as Steps atuais
        #

        pipeline_context.variables["build_context"] = (
            build_context
        )

        pipeline_context.variables["publish_context"] = (
            publish_context
        )

        #
        # Evolução da Engine
        #

        pipeline_context.variables["execution_context"] = (
            build_context
        )

        #
        # Cria a Pipeline
        #

        pipeline = self.__pipeline_factory.create(
            build_context.project,
        )

        #
        # Executa
        #

        return self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=pipeline_context,
        )