"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_setups_use_case.py
Descrição : Caso de uso responsável pela publicação em lote dos
            Setups gerados.
--------------------------------------------------------------------
"""

import json
from datetime import datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.abstractions.setup_network_publisher import (
    SetupNetworkPublisher,
)
from app.abstractions.setup_publication_batch_repository import (
    SetupPublicationBatchRepository,
)
from app.abstractions.setup_publication_log_repository import (
    SetupPublicationLogRepository,
)
from app.models.configuration.app_settings import AppSettings
from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)
from app.models.setup.setup_batch_publish_result import (
    SetupBatchPublishResult,
)
from app.models.setup.setup_publication_batch import (
    SetupPublicationBatch,
)
from app.models.setup.setup_publication_log import SetupPublicationLog


class DefaultPublishSetupsUseCase:
    """Controla a publicação de uma versão de Setup em lote."""

    def __init__(
        self,
        pipeline_execution_repository: PipelineExecutionRepository,
        setup_network_publisher: SetupNetworkPublisher,
        setup_publication_batch_repository: SetupPublicationBatchRepository,
        setup_publication_log_repository: SetupPublicationLogRepository,
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
        if setup_publication_batch_repository is None:
            raise ValueError(
                "SetupPublicationBatchRepository não foi informado."
            )
        if setup_publication_log_repository is None:
            raise ValueError(
                "SetupPublicationLogRepository não foi informado."
            )
        if settings is None:
            raise ValueError("AppSettings não foi informado.")

        self.__pipeline_execution_repository = (
            pipeline_execution_repository
        )
        self.__setup_network_publisher = setup_network_publisher
        self.__batch_repository = setup_publication_batch_repository
        self.__log_repository = setup_publication_log_repository
        self.__settings = settings

    def start(
        self,
        request: SetupBatchPublishRequest,
    ) -> SetupBatchPublishResult:
        """Valida, cria o lote e retorna sem bloquear a publicação."""

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
            request.version,
            request.revision,
        )

        if not source_path.exists():
            raise FileNotFoundError(
                "Diretório local da versão do Setup não encontrado: "
                f"{source_path}"
            )

        if not source_path.is_dir():
            raise NotADirectoryError(
                "A origem da publicação do Setup não é um diretório: "
                f"{source_path}"
            )

        batch_id = uuid4().hex.upper()
        batch = SetupPublicationBatch(
            batch_id=batch_id,
            version=request.version,
            revision=request.revision,
            source_path=source_path,
            destination_path=None,
            status="pending",
            started_at=datetime.now(),
            total_setups=len(project_ids),
            completed_setups=0,
            failed_setups=0,
        )

        self.__batch_repository.save(batch)
        self.__log(
            batch_id=batch_id,
            event_type="BATCH_STARTED",
            message="Publicação em lote criada.",
            details=self.__serialize_start(
                request=request,
                project_ids=project_ids,
            ),
        )

        return SetupBatchPublishResult(
            batch_id=batch_id,
            success=True,
            status="pending",
            message="Publicação em lote iniciada.",
            execution_ids=request.execution_ids,
            project_ids=project_ids,
            source_path=source_path,
            publication=None,
        )

    def execute_batch(
        self,
        request: SetupBatchPublishRequest,
        batch_id: str,
    ) -> SetupBatchPublishResult:
        """Executa a publicação de um lote já criado."""

        if not batch_id:
            raise ValueError("batch_id é obrigatório.")

        batch = self.__batch_repository.get_by_batch_id(batch_id)
        if batch is None:
            raise ValueError(
                f"Lote de publicação não encontrado: {batch_id}"
            )

        timer = perf_counter()
        project_ids = list(request.execution_ids)

        try:
            executions = [
                self.__get_execution(execution_id)
                for execution_id in request.execution_ids
            ]
            project_ids = self.__validate_executions(
                executions=executions,
                request=request,
            )

            batch.status = "running"
            batch.total_setups = len(project_ids)
            self.__update_batch(batch, timer)

            self.__log(
                batch_id=batch_id,
                event_type="NETWORK_PUBLISH_START",
                message="Publicação dos Setups na rede iniciada.",
                details=self.__serialize_project_ids(
                    request.execution_ids,
                    project_ids,
                ),
            )

            for execution_id, project_id in zip(
                request.execution_ids,
                project_ids,
            ):
                self.__log(
                    batch_id=batch_id,
                    event_type="PROJECT_PUBLISH_START",
                    message="Setup aguardando conclusão da cópia.",
                    project_id=project_id,
                    execution_id=execution_id,
                )

            publication = self.__setup_network_publisher.publish(
                project_id="batch",
                source_path=batch.source_path,
                version=request.version,
                revision=request.revision,
            )

            batch.destination_path = publication.destination_path

            if not publication.success:
                batch.status = "failed"
                batch.failed_setups = len(project_ids)
                batch.completed_setups = 0
                batch.message = publication.message

                for execution_id, project_id in zip(
                    request.execution_ids,
                    project_ids,
                ):
                    self.__log(
                        batch_id=batch_id,
                        level="ERROR",
                        event_type="PROJECT_PUBLISH_FAILED",
                        message=publication.message,
                        project_id=project_id,
                        execution_id=execution_id,
                        details=self.__serialize_publication(
                            publication,
                        ),
                    )

                self.__log(
                    batch_id=batch_id,
                    level="ERROR",
                    event_type="NETWORK_PUBLISH_FAILED",
                    message=publication.message,
                    details=self.__serialize_publication(
                        publication,
                    ),
                )

                self.__update_batch(batch, timer)

                return SetupBatchPublishResult(
                    batch_id=batch_id,
                    success=False,
                    status=batch.status,
                    message=publication.message,
                    execution_ids=request.execution_ids,
                    project_ids=project_ids,
                    source_path=batch.source_path,
                    publication=publication,
                )

            batch.status = "completed"
            batch.completed_setups = len(project_ids)
            batch.failed_setups = 0
            batch.message = (
                "Publicação em rede concluída com sucesso para "
                f"{len(project_ids)} projeto(s)."
            )

            for execution_id, project_id in zip(
                request.execution_ids,
                project_ids,
            ):
                self.__log(
                    batch_id=batch_id,
                    event_type="PROJECT_PUBLISH_SUCCESS",
                    message="Setup copiado com sucesso para a rede.",
                    project_id=project_id,
                    execution_id=execution_id,
                    details=self.__serialize_publication(
                        publication,
                    ),
                )

            self.__log(
                batch_id=batch_id,
                event_type="NETWORK_PUBLISH_SUCCESS",
                message=batch.message,
                details=self.__serialize_publication(
                    publication,
                ),
            )

            self.__update_batch(batch, timer)

            return SetupBatchPublishResult(
                batch_id=batch_id,
                success=True,
                status=batch.status,
                message=batch.message,
                execution_ids=request.execution_ids,
                project_ids=project_ids,
                source_path=batch.source_path,
                publication=publication,
            )

        except Exception as exception:
            batch.status = "failed"
            batch.failed_setups = batch.total_setups
            batch.message = (
                f"Falha na publicação em lote: {exception}"
            )
            self.__update_batch(batch, timer)

            self.__log(
                batch_id=batch_id,
                level="ERROR",
                event_type="BATCH_FAILED",
                message=batch.message,
            )

            for execution_id, project_id in zip(
                request.execution_ids,
                project_ids,
            ):
                self.__log(
                    batch_id=batch_id,
                    level="ERROR",
                    event_type="PROJECT_PUBLISH_FAILED",
                    message=batch.message,
                    project_id=project_id,
                    execution_id=execution_id,
                )

            return SetupBatchPublishResult(
                batch_id=batch_id,
                success=False,
                status=batch.status,
                message=batch.message,
                execution_ids=request.execution_ids,
                project_ids=project_ids,
                source_path=batch.source_path,
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
                f"Execução não encontrada: {execution_id}"
            )

        return execution

    @staticmethod
    def __validate_executions(
        executions: list[dict],
        request: SetupBatchPublishRequest,
    ) -> list[str]:
        project_ids: list[str] = []

        for execution in executions:
            execution_id = execution.get("execution_id", "")

            if execution.get("status") != "completed":
                raise ValueError(
                    f"A execução {execution_id} ainda não está concluída."
                )

            if execution.get("success") is not True:
                raise ValueError(
                    f"A execução {execution_id} não foi concluída "
                    "com sucesso."
                )

            execution_version = execution.get("version")

            if execution_version != request.version:
                raise ValueError(
                    f"A execução {execution_id} pertence à versão "
                    f"{execution_version!r}, mas foi solicitada a "
                    f"versão {request.version!r}."
                )

            project_id = execution.get("project_id", "")

            if not project_id:
                raise ValueError(
                    f"A execução {execution_id} não possui project_id."
                )

            if project_id in project_ids:
                raise ValueError(
                    f"O projeto {project_id} possui mais de uma execução "
                    "na publicação solicitada."
                )

            project_ids.append(project_id)

        return project_ids

    def __update_batch(
        self,
        batch: SetupPublicationBatch,
        timer: float,
    ) -> None:
        batch.elapsed_seconds = perf_counter() - timer

        if batch.status in {"completed", "failed"}:
            batch.finished_at = datetime.now()

        self.__batch_repository.update(batch)

    def __log(
        self,
        batch_id: str,
        event_type: str,
        message: str,
        level: str = "INFO",
        details: str | None = None,
        project_id: str | None = None,
        execution_id: str | None = None,
    ) -> None:
        self.__log_repository.save(
            SetupPublicationLog(
                batch_id=batch_id,
                timestamp=datetime.now(),
                level=level,
                event_type=event_type,
                project_id=project_id,
                execution_id=execution_id,
                message=message,
                details=details,
            )
        )

    @staticmethod
    def __serialize_start(
        request: SetupBatchPublishRequest,
        project_ids: list[str],
    ) -> str:
        return json.dumps(
            {
                "execution_ids": request.execution_ids,
                "project_ids": project_ids,
                "version": request.version,
                "revision": request.revision,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def __serialize_project_ids(
        execution_ids: list[str],
        project_ids: list[str],
    ) -> str:
        return json.dumps(
            {
                "execution_ids": execution_ids,
                "project_ids": project_ids,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def __serialize_publication(
        publication: object,
    ) -> str:
        data = {
            "success": getattr(publication, "success", None),
            "destination_path": str(
                getattr(publication, "destination_path", None)
            ),
            "backup_path": str(
                getattr(publication, "backup_path", None)
            ),
            "backup_created": getattr(
                publication,
                "backup_created",
                False,
            ),
            "backup_removed": getattr(
                publication,
                "backup_removed",
                False,
            ),
            "files_copied": getattr(
                publication,
                "files_copied",
                0,
            ),
            "duration_seconds": getattr(
                publication,
                "duration_seconds",
                0.0,
            ),
        }

        return json.dumps(
            data,
            ensure_ascii=False,
        )

    def __resolve_source_path(
        self,
        version: str,
        revision: int,
    ) -> Path:
        return (
            Path(self.__settings.setup.output_root)
            / f"{version}.{revision}"
        )
