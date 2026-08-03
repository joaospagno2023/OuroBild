"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_build_use_case.py
Descrição : Responsável por iniciar uma execução de Build.
--------------------------------------------------------------------
"""

from app.abstractions.pipeline_factory import PipelineFactory
from app.factories.build_context_factory import (
    BuildContextFactory,
)
from app.factories.build_environment_builder_factory import (
    BuildEnvironmentBuilderFactory,
)
from app.models.build.build_request import BuildRequest
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.pipeline_result import PipelineResult
from app.pipeline.runner.pipeline_runner import PipelineRunner


class ExecuteBuildUseCase:
    """
    Responsável por iniciar uma execução de Build.
    """

    def __init__(
        self,
        build_context_factory: BuildContextFactory,
        pipeline_factory: PipelineFactory,
    ) -> None:

        self.__build_context_factory = (
            build_context_factory
        )

        self.__pipeline_factory = (
            pipeline_factory
        )

        self.__builder_factory = (
            BuildEnvironmentBuilderFactory()
        )

    def execute(
        self,
        request: BuildRequest,
    ) -> PipelineResult:
        """
        Executa uma Build utilizando a Pipeline atual.
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
        # Resolve os caminhos
        #

        builder = self.__builder_factory.create(
            build_context.environment,
        )

        builder.build(
            build_context,
        )

        #
        # Adaptador temporário
        #

        pipeline_context = PipelineContext()

        #
        # Compatibilidade com a Engine atual
        #

        pipeline_context.variables["project"] = (
            build_context.project
        )

        pipeline_context.variables["project_id"] = (
            build_context.project.id
        )

        #
        # Nova Build Engine
        #

        pipeline_context.variables["request"] = (
            build_context.request
        )

        pipeline_context.variables["environment"] = (
            build_context.environment
        )

        pipeline_context.variables["paths"] = (
            build_context.paths
        )

        pipeline_context.variables["build_context"] = (
            build_context
        )

        #
        # Executa a Pipeline
        #

        pipeline = self.__pipeline_factory.create(
            build_context.project,
        )

        runner = PipelineRunner()

        return runner.execute(
            pipeline=pipeline,
            context=pipeline_context,
        )