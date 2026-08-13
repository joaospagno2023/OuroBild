"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_publish_use_case.py
Descrição : Responsável por iniciar uma execução de Publish.
--------------------------------------------------------------------
"""

from datetime import datetime

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

from app.models.publish.publish_batch_result import (
    PublishBatchResult,
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


class ExecutePublishUseCase:
    """
    Responsável por iniciar uma execução de Publish.
    """

    def __init__(
        self,
        build_context_factory: BuildContextFactory,
        publish_context_factory: PublishContextFactory,
        pipeline_factory: PipelineFactory,
        solution_locator: SolutionLocatorService,
        pipeline_runner: PipelineRunner,
        project_repository: ProjectRepository,
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

        self.__project_repository = (
            project_repository
        )

        self.__builder_factory = (
            BuildEnvironmentBuilderFactory(
                solution_locator=solution_locator,
            )
        )

    def execute(
        self,
        request: PublishRequest,
    ) -> PipelineResult | PublishBatchResult:
        """
        Executa uma Pipeline de Publish.

        Quando project_id é informado, executa somente
        o projeto solicitado.

        Quando project_id não é informado, executa todos
        os projetos habilitados, em sequência.

        A execução é interrompida imediatamente caso
        qualquer projeto falhe.
        """

        #
        # Normaliza e valida o ambiente.
        #

        request = self.__normalize_request(
            request,
        )

        #
        # Publish individual
        #

        if request.project_id is not None:

            return self.__execute_project(
                request=request,
            )

        #
        # Publish de todos os projetos
        #

        started_at = datetime.now()

        batch_result = PublishBatchResult(
            started_at=started_at,
        )

        projects = (
            self.__project_repository.get_all()
        )

        for project in projects:

            #
            # Projetos desabilitados não participam
            # da execução.
            #

            if not project.enabled:
                continue

            #
            # Cria uma requisição específica para
            # o projeto atual.
            #
            # Mantemos workspace, version, revision,
            # environment_id e demais opções de Publish.
            #

            project_request = request.model_copy(
                update={
                    "project_id": project.id,
                },
            )

            #
            # Executa o projeto.
            #

            result = self.__execute_project(
                request=project_request,
            )

            #
            # Preserva o resultado completo do projeto.
            #

            batch_result.projects.append(
                result,
            )

            #
            # Qualquer falha interrompe a execução
            # imediatamente.
            #

            if not result.success:

                batch_result.success = False

                batch_result.message = (
                    "Publish interrompido devido "
                    "a uma falha no projeto."
                )

                batch_result.failed_project = (
                    project.id
                )

                batch_result.finished_at = (
                    datetime.now()
                )

                batch_result.elapsed_seconds = (
                    batch_result.finished_at
                    - batch_result.started_at
                ).total_seconds()

                return batch_result

        #
        # Todos os projetos habilitados foram
        # executados com sucesso.
        #

        batch_result.success = True

        batch_result.message = (
            "Publish concluído com sucesso."
        )

        batch_result.finished_at = (
            datetime.now()
        )

        batch_result.elapsed_seconds = (
            batch_result.finished_at
            - batch_result.started_at
        ).total_seconds()

        return batch_result

    def __normalize_request(
        self,
        request: PublishRequest,
    ) -> PublishRequest:
        """
        Normaliza a requisição de Publish.

        O workspace determina o ambiente:

        production
            -> environment_id = production

        versioned
            -> environment_id = versioned
            -> exige version e revision
        """

        #
        # Workspace informado.
        #

        if request.workspace is not None:

            workspace = (
                request.workspace
                .strip()
                .lower()
            )

            #
            # Production.
            #

            if workspace == "production":

                return request.model_copy(
                    update={
                        "environment_id": "production",
                    },
                )

            #
            # Versionado.
            #

            if workspace == "versioned":

                if not request.version:

                    raise ValueError(
                        "A versão é obrigatória "
                        "para o workspace 'versioned'."
                    )

                if request.revision is None:

                    raise ValueError(
                        "A revisão é obrigatória "
                        "para o workspace 'versioned'."
                    )

                return request.model_copy(
                    update={
                        "environment_id": "versioned",
                    },
                )

            #
            # Workspace inválido.
            #

            raise ValueError(
                f"Workspace não suportado: "
                f"{request.workspace}"
            )

        #
        # Compatibilidade com chamadas antigas
        # que já enviam environment_id.
        #

        if request.environment_id:

            #
            # Se for versioned, exige version
            # e revision.
            #

            if (
                request.environment_id
                == "versioned"
            ):

                if not request.version:

                    raise ValueError(
                        "A versão é obrigatória "
                        "para o ambiente 'versioned'."
                    )

                if request.revision is None:

                    raise ValueError(
                        "A revisão é obrigatória "
                        "para o ambiente 'versioned'."
                    )

            return request

        #
        # Nenhum ambiente informado.
        #

        raise ValueError(
            "O workspace ou environment_id "
            "deve ser informado."
        )

    def __execute_project(
        self,
        request: PublishRequest,
    ) -> PipelineResult:
        """
        Executa o Publish de um único projeto.
        """

        #
        # Cria o BuildRequest.
        #
        # A versão e a revisão são preservadas
        # para o ambiente versionado.
        #

        build_request = BuildRequest(
            project_id=request.project_id,
            environment_id=request.environment_id,
            version=request.version,
            revision=request.revision,
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
        # Cria o PublishContext.
        #

        publish_context = (
            self.__publish_context_factory.create(
                request,
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
        # Contexto necessário pelas Steps de Build.
        #

        pipeline_context.variables["build_context"] = (
            build_context
        )

        #
        # Contexto necessário pelas Steps de Publish.
        #

        pipeline_context.variables["publish_context"] = (
            publish_context
        )

        #
        # Contexto geral da execução.
        #

        pipeline_context.variables["execution_context"] = (
            build_context
        )

        #
        # Cria a Pipeline.
        #

        pipeline = self.__pipeline_factory.create(
            build_context.project,
        )

        #
        # Executa.
        #

        return self.__pipeline_runner.execute(
            pipeline=pipeline,
            context=pipeline_context,
        )