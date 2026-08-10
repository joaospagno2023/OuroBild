"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_publish_use_case.py
Descrição : Responsável por iniciar uma execução de Publish.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import PipelineFactory
from app.factories.build_environment_builder_factory import (
    BuildEnvironmentBuilderFactory,
)
from app.factories.publish_context_factory import (
    PublishContextFactory,
)
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.pipeline_result import PipelineResult
from app.models.publish.publish_request import PublishRequest
from app.pipeline.runner.pipeline_runner import PipelineRunner
from app.services.workspace.solution_locator_service import (
    SolutionLocatorService,
)

class ExecutePublishUseCase:
    """
    Responsável por iniciar uma execução de Publish.
    """

    def __init__(
        self,
        publish_context_factory: PublishContextFactory,
        pipeline_factory: PipelineFactory,
        solution_locator: SolutionLocatorService,
        pipeline_runner: PipelineRunner,
    ) -> None:

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
        request: PublishRequest,
    ) -> PipelineResult:
        """
        Executa uma Pipeline de Publish.
        """

        #
        # Cria o PublishContext
        #

        publish_context = (
            self.__publish_context_factory.create(
                request,
            )
        )

        #
        # Resolve os caminhos do ambiente
        #

        builder = self.__builder_factory.create(
            publish_context.environment,
        )

        builder.build(
            publish_context,
        )

        #
        # Cria o PipelineContext
        #

        pipeline_context = PipelineContext()

        pipeline_context.variables["project"] = (
            publish_context.project
        )

        pipeline_context.variables["project_id"] = (
            publish_context.project.id
        )

        pipeline_context.variables["request"] = (
            publish_context.request
        )

        pipeline_context.variables["environment"] = (
            publish_context.environment
        )

        pipeline_context.variables["paths"] = (
            publish_context.paths
        )

        #
        # Compatibilidade com as Steps atuais
        #

        pipeline_context.variables["publish_context"] = (
            publish_context
        )

        #
        # Evolução da Engine
        #

        pipeline_context.variables["execution_context"] = (
            publish_context
        )

        #
        # Cria a Pipeline
        #

        pipeline = self.__pipeline_factory.create(
            publish_context.project,
        )

        #
        # Executa
        #

        return self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=pipeline_context,
        )