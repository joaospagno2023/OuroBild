"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_build_use_case.py
Descrição : Responsável por iniciar uma execução de Build.
--------------------------------------------------------------------
"""

from pathlib import Path
from uuid import uuid4

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
from app.utils.pipeline_logger import (
    PipelineLogger,
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
        execution_id: str | None = None,
    ) -> PipelineResult:
        """
        Executa uma Pipeline de Build.

        Quando a execução já pertence a uma Pipeline externa,
        o execution_id existente é preservado.

        Quando o Build é executado isoladamente, como ocorre
        durante uma geração direta de Setup, um novo execution_id
        é criado para garantir a rastreabilidade e a persistência
        correta do resultado.
        """

        if request is None:
            raise ValueError(
                "BuildRequest não foi informado."
            )

        current_execution_id = (
            execution_id
            or uuid4().hex.upper()
        )

        #
        # ============================================================
        # Diagnóstico - início
        # ============================================================
        #

        PipelineLogger.info(
            "BUILD DIAGNOSTICO - INICIO"
        )

        PipelineLogger.info(
            f"Projeto...............: {request.project_id}"
        )

        PipelineLogger.info(
            f"Ambiente..............: {request.environment_id}"
        )

        PipelineLogger.info(
            f"Versao................: {request.version}"
        )

        PipelineLogger.info(
            f"Revisao................: {request.revision}"
        )

        PipelineLogger.info(
            f"ExecutionId............: {current_execution_id}"
        )

        #
        # ============================================================
        # BuildContext
        # ============================================================
        #

        build_context = (
            self.__build_context_factory.create(
                request,
            )
        )

        #
        # ============================================================
        # Resolve Build
        # ============================================================
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
        # ============================================================
        # Diagnóstico - caminhos do Build
        # ============================================================
        #

        PipelineLogger.info(
            "BUILD DIAGNOSTICO - CAMINHOS RESOLVIDOS"
        )

        PipelineLogger.info(
            f"Resolver..............: "
            f"{build_context.environment.resolver}"
        )

        PipelineLogger.info(
            f"WorkspaceRoot.........: "
            f"{build_context.paths.workspace_root}"
        )

        PipelineLogger.info(
            f"ProjectFile...........: "
            f"{build_context.paths.project_file}"
        )

        PipelineLogger.info(
            f"SourceRoot............: "
            f"{build_context.paths.source_root}"
        )

        PipelineLogger.info(
            f"PublishRoot...........: "
            f"{build_context.paths.publish_root}"
        )

        self.__log_directory_contents(
            title=(
                "BUILD - PUBLISH ROOT APOS BUILD"
            ),
            directory=Path(
                build_context.paths.publish_root,
            ),
        )

        #
        # ============================================================
        # Diretório de saída do Publish
        # ============================================================
        #

        output_directory = None

        if (
            build_context.environment.resolver
            == "versioned"
        ):
            output_directory = str(
                build_context.paths.publish_root
            )

        #
        # ============================================================
        # Diagnóstico - PublishRequest
        # ============================================================
        #

        PipelineLogger.info(
            "PUBLISH DIAGNOSTICO - REQUEST"
        )

        PipelineLogger.info(
            f"Resolver..............: "
            f"{build_context.environment.resolver}"
        )

        PipelineLogger.info(
            f"OutputDirectory.......: "
            f"{output_directory}"
        )

        PipelineLogger.info(
            f"Version...............: "
            f"{request.version}"
        )

        PipelineLogger.info(
            f"Revision..............: "
            f"{request.revision}"
        )

        #
        # ============================================================
        # PublishRequest
        # ============================================================
        #

        publish_request = PublishRequest(
            project_id=(
                build_context.project.id
            ),
            environment_id=(
                build_context.environment.id
            ),
            version=request.version,
            revision=request.revision,
            output_directory=output_directory,
            publish_profile=(
                build_context.project.publish_profile
            ),
        )

        #
        # ============================================================
        # PublishContext
        # ============================================================
        #

        publish_context = (
            self.__publish_context_factory.create(
                publish_request,
            )
        )

        #
        # ============================================================
        # Resolve caminhos do Publish
        # ============================================================
        #

        publish_builder = (
            self.__builder_factory.create(
                publish_context.environment,
            )
        )

        #
        # ============================================================
        # Diagnóstico - antes do Publish
        # ============================================================
        #

        PipelineLogger.info(
            "PUBLISH DIAGNOSTICO - ANTES DO PUBLISH"
        )

        PipelineLogger.info(
            f"ProjectFile...........: "
            f"{publish_context.paths.project_file}"
        )

        PipelineLogger.info(
            f"Request.OutputDir.....: "
            f"{publish_context.request.output_directory}"
        )

        PipelineLogger.info(
            f"Build.PublishRoot.....: "
            f"{build_context.paths.publish_root}"
        )

        #
        # ============================================================
        # Executa Publish
        # ============================================================
        #

        publish_builder.build(
            publish_context,
        )

        #
        # ============================================================
        # Diagnóstico - após Publish
        # ============================================================
        #

        PipelineLogger.info(
            "PUBLISH DIAGNOSTICO - APOS PUBLISH"
        )

        PipelineLogger.info(
            f"Request.OutputDir.....: "
            f"{publish_context.request.output_directory}"
        )

        PipelineLogger.info(
            f"Build.PublishRoot.....: "
            f"{build_context.paths.publish_root}"
        )

        #
        # ============================================================
        # Verificação do diretório final
        # ============================================================
        #

        publish_output_directory = (
            publish_context.request.output_directory
        )

        if publish_output_directory:
            publish_output_path = Path(
                publish_output_directory
            )
        else:
            publish_output_path = Path(
                build_context.paths.publish_root
            )

        self.__log_directory_contents(
            title="PUBLISH - RESULTADO FINAL",
            directory=publish_output_path,
        )

        #
        # ============================================================
        # PipelineContext
        # ============================================================
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

        pipeline_context.variables["build_context"] = (
            build_context
        )

        pipeline_context.variables["publish_context"] = (
            publish_context
        )

        pipeline_context.variables["execution_context"] = (
            build_context
        )

        #
        # ============================================================
        # Pipeline
        # ============================================================
        #

        pipeline = self.__pipeline_factory.create(
            build_context.project,
        )

        #
        # ============================================================
        # Execução
        # ============================================================
        #

        return self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=pipeline_context,
            execution_id=current_execution_id,
            project_id=(
                build_context.project.id
            ),
        )

    @staticmethod
    def __log_directory_contents(
        title: str,
        directory: Path,
    ) -> None:
        """
        Registra no log o conteúdo de um diretório para diagnóstico.
        """

        directory = Path(directory)

        PipelineLogger.info(
            "=" * 80
        )

        PipelineLogger.info(
            title
        )

        PipelineLogger.info(
            f"Diretorio.............: {directory}"
        )

        if not directory.exists():
            PipelineLogger.info(
                "Diretorio existe......: False"
            )

            PipelineLogger.info(
                "Arquivos..............: 0"
            )

            PipelineLogger.info(
                "=" * 80
            )

            return

        if not directory.is_dir():
            PipelineLogger.info(
                "Diretorio existe......: True"
            )

            PipelineLogger.info(
                "Diretorio valido......: False"
            )

            PipelineLogger.info(
                "=" * 80
            )

            return

        files = sorted(
            [
                path
                for path in directory.rglob("*")
                if path.is_file()
            ],
            key=lambda path: str(
                path
            ).lower(),
        )

        PipelineLogger.info(
            "Diretorio existe......: True"
        )

        PipelineLogger.info(
            f"Arquivos..............: "
            f"{len(files)}"
        )

        for file_path in files:
            try:
                relative_path = (
                    file_path.relative_to(
                        directory
                    )
                )
            except ValueError:
                relative_path = file_path

            PipelineLogger.info(
                f"ARQUIVO...............: "
                f"{relative_path}"
            )

        PipelineLogger.info(
            "=" * 80
        )