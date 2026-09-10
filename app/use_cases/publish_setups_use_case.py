"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_setups_use_case.py
Descrição : Caso de uso responsável pela publicação em lote dos
            Setups gerados.
--------------------------------------------------------------------
"""

from pathlib import Path
from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)

from app.abstractions.setup_network_publisher import (
    SetupNetworkPublisher,
)

from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)

from app.models.setup.setup_batch_publish_result import (
    SetupBatchPublishResult,
)


class DefaultPublishSetupsUseCase:
    """
    Valida uma geração completa e publica a versão na rede.

    A publicação somente pode começar quando todas as execuções
    informadas estiverem concluídas com sucesso.
    """

    def __init__(
        self,
        pipeline_execution_repository: PipelineExecutionRepository,
        setup_network_publisher: SetupNetworkPublisher,
        settings: AppSettings,
    ) -> None:
        if pipeline_execution_repository is None:
            raise ValueError(
                "PipelineExecutionRepository não foi informado."
            )

        if setup_network_publisher is None:
            raise ValueError(
                "SetupNetworkPublisher não foi informado."
            )

        if settings is None:
            raise ValueError(
                "AppSettings não foi informado."
            )

        self.__pipeline_execution_repository = (
            pipeline_execution_repository
        )
        self.__setup_network_publisher = (
            setup_network_publisher
        )
        self.__settings = settings

    def execute(
        self,
        request: SetupBatchPublishRequest,
    ) -> SetupBatchPublishResult:
        """
        Publica uma versão de Setup somente após validar
        todas as execuções informadas.
        """

        try:
            self.__validate_request(request)

            executions = [
                self.__get_execution(execution_id)
                for execution_id in request.execution_ids
            ]

            project_ids = self.__validate_executions(
                executions=executions,
                request=request,
            )

            source_path = self.__resolve_source_path(
                version=request.version,
                revision=request.revision,
            )

            if not source_path.exists():
                raise FileNotFoundError(
                    "Diretório local da versão do Setup não encontrado: "
                    f"{source_path}"
                )

            if not source_path.is_dir():
                raise NotADirectoryError(
                    "A origem da publicação do Setup não é "
                    f"um diretório: {source_path}"
                )

            publication = self.__setup_network_publisher.publish(
                project_id="batch",
                source_path=source_path,
                version=request.version,
                revision=request.revision,
            )

            if not publication.success:
                return SetupBatchPublishResult(
                    success=False,
                    message=publication.message,
                    execution_ids=request.execution_ids,
                    project_ids=project_ids,
                    source_path=source_path,
                    publication=publication,
                )

            return SetupBatchPublishResult(
                success=True,
                message=(
                    f"Publicação em rede concluída com sucesso "
                    f"para {len(project_ids)} projeto(s)."
                ),
                execution_ids=request.execution_ids,
                project_ids=project_ids,
                source_path=source_path,
                publication=publication,
            )

        except Exception as exception:
            return SetupBatchPublishResult(
                success=False,
                message=(
                    "Falha na publicação em lote: "
                    f"{exception}"
                ),
                execution_ids=(
                    request.execution_ids
                    if request is not None
                    else []
                ),
                project_ids=[],
                source_path=(
                    self.__resolve_source_path(
                        request.version,
                        request.revision,
                    )
                    if request is not None
                    and request.version
                    and request.revision >= 0
                    else None
                ),
                publication=None,
            )

    @staticmethod
    def __validate_request(
        request: SetupBatchPublishRequest,
    ) -> None:
        if request is None:
            raise ValueError(
                "SetupBatchPublishRequest não foi informado."
            )

        if not request.execution_ids:
            raise ValueError(
                "Nenhuma execução foi informada para publicação."
            )

        normalized_ids = [
            execution_id.strip()
            for execution_id in request.execution_ids
        ]

        if any(not execution_id for execution_id in normalized_ids):
            raise ValueError(
                "Existe execution_id inválido na solicitação."
            )

        if len(set(normalized_ids)) != len(normalized_ids):
            raise ValueError(
                "Existem execution_ids duplicados na solicitação."
            )

        if not request.version.strip():
            raise ValueError(
                "A versão do Setup não foi informada."
            )

        if request.revision < 0:
            raise ValueError(
                "A revisão do Setup não pode ser negativa."
            )

    def __get_execution(
        self,
        execution_id: str,
    ) -> dict:
        execution = (
            self.__pipeline_execution_repository.get_by_execution_id(
                execution_id,
            )
        )

        if execution is None:
            raise ValueError(
                "Execução não encontrada: "
                f"{execution_id}"
            )

        return execution

    @staticmethod
    def __validate_executions(
        executions: list[dict],
        request: SetupBatchPublishRequest,
    ) -> list[str]:
        project_ids: list[str] = []

        for execution in executions:
            execution_id = execution.get(
                "execution_id",
                "",
            )

            if execution.get("status") != "completed":
                raise ValueError(
                    "A execução "
                    f"{execution_id} ainda não está concluída."
                )

            if execution.get("success") is not True:
                raise ValueError(
                    "A execução "
                    f"{execution_id} não foi concluída com sucesso."
                )

            execution_version = execution.get(
                "version",
            )

            if execution_version != request.version:
                raise ValueError(
                    "A execução "
                    f"{execution_id} pertence à versão "
                    f"{execution_version!r}, mas foi solicitada "
                    f"a versão {request.version!r}."
                )

            project_id = execution.get(
                "project_id",
                "",
            )

            if not project_id:
                raise ValueError(
                    "A execução "
                    f"{execution_id} não possui project_id."
                )

            if project_id in project_ids:
                raise ValueError(
                    "O projeto "
                    f"{project_id} possui mais de uma execução "
                    "na publicação solicitada."
                )

            project_ids.append(project_id)

        return project_ids

    def __resolve_source_path(
        self,
        version: str,
        revision: int,
    ) -> Path:
        return (
            Path(self.__settings.setup.output_root)
            / f"{version}.{revision}"
        )
