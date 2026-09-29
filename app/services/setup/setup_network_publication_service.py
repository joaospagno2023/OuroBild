"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_network_publication_service.py
Descrição : Gerencia a publicação assíncrona de Setups na rede.
--------------------------------------------------------------------
"""

import os
import time
from datetime import datetime
from threading import Lock
from uuid import uuid4

from app.models.configuration.app_settings import AppSettings
from app.models.setup.setup_publication_request import (
    SetupPublicationRequest,
)
from app.models.setup.setup_republish_request import (
    SetupRepublishRequest,
)
from app.models.setup.setup_publication_project_status import (
    SetupPublicationProjectStatus,
)
from app.models.setup.setup_publication_start_result import (
    SetupPublicationStartResult,
)
from app.models.setup.setup_publication_status_result import (
    SetupPublicationStatusResult,
)
from app.services.pipeline.pipeline_execution_service import (
    get_pipeline_execution_service,
)
from app.services.setup.network_setup_publisher import (
    DefaultSetupNetworkPublisher,
    SetupNetworkPublishProgressCallback,
)


class SetupNetworkPublicationService:
    """Executa e acompanha uma publicação de Setup em background."""

    def __init__(
        self,
        settings: AppSettings,
        publisher: DefaultSetupNetworkPublisher,
    ) -> None:
        self.__settings = settings
        self.__publisher = publisher
        self.__lock = Lock()
        self.__states: dict[str, SetupPublicationStatusResult] = {}

    def start(
        self,
        request: SetupPublicationRequest,
    ) -> SetupPublicationStartResult:
        execution_ids = [
            execution_id.strip()
            for execution_id in request.execution_ids
            if execution_id.strip()
        ]

        if not execution_ids:
            raise ValueError(
                "Nenhuma execução foi informada para publicação."
            )

        version = request.version.strip()

        if not version:
            raise ValueError(
                "A versão é obrigatória para publicação na rede."
            )

        if request.revision < 0:
            raise ValueError(
                "A revisão não pode ser negativa."
            )

        execution_service = get_pipeline_execution_service()
        executions = []

        for execution_id in execution_ids:
            execution = execution_service.get(execution_id)

            if execution is None:
                raise ValueError(
                    f"Execução não encontrada: {execution_id}"
                )

            if (
                execution.status.value != "completed"
                or execution.success is not True
            ):
                raise ValueError(
                    "A publicação só pode ser iniciada quando "
                    "todas as gerações selecionadas tiverem sucesso. "
                    f"Execução: {execution_id}"
                )

            executions.append(execution)

        batch_id = uuid4().hex.upper()
        project_ids = [
            execution.project_id
            for execution in executions
        ]

        source_path = (
            self.__settings.setup.output_root
            / f"{version}.{request.revision}"
        )

        state = SetupPublicationStatusResult(
            batch_id=batch_id,
            status="pending",
            success=None,
            message="Publicação aguardando início.",
            total=0,
            completed=0,
            failed=0,
            progress_percent=0,
            current_file=None,
            current_file_index=0,
            total_files=0,
            projects=[
                SetupPublicationProjectStatus(
                    project_id=execution.project_id,
                    execution_id=execution.execution_id,
                    status="waiting",
                    message="Aguardando publicação.",
                )
                for execution in executions
            ],
        )

        with self.__lock:
            self.__states[batch_id] = state

        import threading

        thread = threading.Thread(
            target=self.__run,
            args=(
                batch_id,
                execution_ids,
                project_ids,
                source_path,
                version,
                request.revision,
            ),
            daemon=True,
            name=f"ourobuild-setup-publish-{batch_id[:8]}",
        )
        thread.start()

        return SetupPublicationStartResult(
            batch_id=batch_id,
            success=True,
            status="pending",
            message="Publicação dos Setups iniciada.",
            execution_ids=execution_ids,
            project_ids=project_ids,
            source_path=str(source_path),
        )

    def start_republish(
        self,
        request: SetupRepublishRequest,
    ) -> SetupPublicationStartResult:
        """
        Copia para a rede Setups já gerados, sem gerá-los de novo.

        Regra: só é permitido até N minutos (padrão 5) após a
        geração, medido pela data de criação do arquivo mais
        recente de Client/Cliente e Server. Fora desse prazo a
        cópia é recusada com um aviso.
        """

        version = request.version.strip()

        if not version:
            raise ValueError(
                "A versão é obrigatória para publicação na rede."
            )

        if request.revision < 0:
            raise ValueError(
                "A revisão não pode ser negativa."
            )

        source_path = (
            self.__settings.setup.output_root
            / f"{version}.{request.revision}"
        )

        def refused(message: str) -> SetupPublicationStartResult:
            return SetupPublicationStartResult(
                batch_id="",
                success=False,
                status="refused",
                message=message,
                execution_ids=[],
                project_ids=[],
                source_path=str(source_path),
            )

        if not source_path.is_dir():
            return refused(
                "Pasta local do Setup não encontrada: "
                f"{source_path}. Gere os Setups novamente."
            )

        client_path = source_path / "Client"

        if not client_path.is_dir():
            client_path = source_path / "Cliente"

        server_path = source_path / "Server"

        if not client_path.is_dir() or not server_path.is_dir():
            return refused(
                "A pasta local não possui Client/Cliente e Server. "
                "Gere os Setups novamente."
            )

        newest = self.__newest_creation_timestamp(
            client_path,
            server_path,
        )

        if newest is None:
            return refused(
                "Nenhum arquivo foi encontrado na pasta local do "
                "Setup. Gere os Setups novamente."
            )

        max_age_seconds = self.__max_age_seconds()
        age_seconds = time.time() - newest

        if age_seconds > max_age_seconds:
            return refused(
                "Cópia não permitida: ela só pode ser feita até "
                f"{max_age_seconds // 60:g} minuto(s) após a geração. "
                "Os arquivos foram gerados em "
                f"{datetime.fromtimestamp(newest):%d/%m/%Y %H:%M:%S} "
                f"(há {int(age_seconds // 60)} min "
                f"{int(age_seconds % 60)} s). "
                "Gere os Setups novamente."
            )

        batch_id = uuid4().hex.upper()

        state = SetupPublicationStatusResult(
            batch_id=batch_id,
            status="pending",
            success=None,
            message="Publicação aguardando início.",
            total=0,
            completed=0,
            failed=0,
            progress_percent=0,
            current_file=None,
            current_file_index=0,
            total_files=0,
            projects=[],
        )

        with self.__lock:
            self.__states[batch_id] = state

        import threading

        thread = threading.Thread(
            target=self.__run,
            args=(
                batch_id,
                [],
                [],
                source_path,
                version,
                request.revision,
            ),
            daemon=True,
            name=f"ourobuild-setup-republish-{batch_id[:8]}",
        )
        thread.start()

        return SetupPublicationStartResult(
            batch_id=batch_id,
            success=True,
            status="pending",
            message="Cópia dos Setups já gerados iniciada.",
            execution_ids=[],
            project_ids=[],
            source_path=str(source_path),
        )

    @staticmethod
    def __max_age_seconds() -> float:
        """Prazo máximo, em segundos, entre a geração e a cópia."""

        try:
            minutes = float(
                os.environ.get(
                    "OUROBUILD_REPUBLISH_MAX_AGE_MINUTES",
                    "5",
                )
            )
        except ValueError:
            minutes = 5.0

        return max(minutes, 0.0) * 60

    @staticmethod
    def __newest_creation_timestamp(
        *roots,
    ) -> float | None:
        """
        Data de criação do arquivo mais recente sob as pastas
        informadas. No Windows usa a data de criação; nos demais
        sistemas, a de modificação.
        """

        newest: float | None = None

        for root in roots:
            for current, _, files in os.walk(root):
                for name in files:
                    try:
                        info = os.stat(
                            os.path.join(current, name)
                        )
                    except OSError:
                        continue

                    created = getattr(
                        info,
                        "st_birthtime",
                        None,
                    )

                    if created is None:
                        created = (
                            info.st_ctime
                            if os.name == "nt"
                            else info.st_mtime
                        )

                    if newest is None or created > newest:
                        newest = created

        return newest

    def get(
        self,
        batch_id: str,
    ) -> SetupPublicationStatusResult | None:
        with self.__lock:
            state = self.__states.get(batch_id)

            if state is None:
                return None

            return state.model_copy(deep=True)

    def __run(
        self,
        batch_id: str,
        execution_ids: list[str],
        project_ids: list[str],
        source_path,
        version: str,
        revision: int,
    ) -> None:
        self.__update(
            batch_id,
            status="running",
            message="Preparando a cópia dos Setups para a rede.",
            projects=[
                SetupPublicationProjectStatus(
                    project_id=project_id,
                    execution_id=execution_id,
                    status="publishing",
                    message="Publicando Setup na rede.",
                )
                for project_id, execution_id in zip(
                    project_ids,
                    execution_ids,
                )
            ],
        )

        def progress_callback(
            current_file_index: int,
            total_files: int,
            current_file: str,
            progress_percent: int,
        ) -> None:
            self.__update(
                batch_id,
                total=total_files,
                total_files=total_files,
                completed=current_file_index,
                current_file_index=current_file_index,
                current_file=current_file,
                progress_percent=progress_percent,
                message=(
                    f"Copiando {current_file_index}/{total_files} "
                    f"{current_file}"
                ),
            )

        try:
            result = self.__publisher.publish(
                project_id=(
                    project_ids[0]
                    if len(project_ids) == 1
                    else "batch"
                ),
                source_path=source_path,
                version=version,
                revision=revision,
                progress_callback=progress_callback,
            )

            if result.success:
                self.__update(
                    batch_id,
                    status="completed",
                    success=True,
                    message=result.message,
                    completed=result.files_copied,
                    failed=0,
                    progress_percent=100,
                    current_file_index=result.files_copied,
                    total_files=result.files_copied,
                    projects=[
                        SetupPublicationProjectStatus(
                            project_id=project_id,
                            execution_id=execution_id,
                            status="success",
                            message="Setup publicado com sucesso.",
                        )
                        for project_id, execution_id in zip(
                            project_ids,
                            execution_ids,
                        )
                    ],
                )
                return

            self.__update(
                batch_id,
                status="failed",
                success=False,
                message=result.message,
                failed=1,
                projects=[
                    SetupPublicationProjectStatus(
                        project_id=project_id,
                        execution_id=execution_id,
                        status="error",
                        message=result.message,
                    )
                    for project_id, execution_id in zip(
                        project_ids,
                        execution_ids,
                    )
                ],
            )

        except Exception as exception:
            self.__update(
                batch_id,
                status="failed",
                success=False,
                message=(
                    "Falha ao publicar os Setups na rede: "
                    f"{exception}"
                ),
                failed=1,
                projects=[
                    SetupPublicationProjectStatus(
                        project_id=project_id,
                        execution_id=execution_id,
                        status="error",
                        message=str(exception),
                    )
                    for project_id, execution_id in zip(
                        project_ids,
                        execution_ids,
                    )
                ],
            )

    def __update(
        self,
        batch_id: str,
        **changes: object,
    ) -> None:
        with self.__lock:
            state = self.__states.get(batch_id)

            if state is None:
                return

            for name, value in changes.items():
                setattr(state, name, value)
