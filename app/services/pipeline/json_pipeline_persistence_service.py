"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_pipeline_persistence_service.py
Descrição : Implementação responsável por persistir uma Pipeline
            em formato JSON.
--------------------------------------------------------------------
"""

import json
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from uuid import uuid4

from app.abstractions.pipeline_persistence_service import (
    PipelinePersistenceService,
)
from app.models.pipeline.pipeline_result import (
    PipelineResult,
)
from app.models.configuration.app_settings import (
    AppSettings,
)


class JsonPipelinePersistenceService(
    PipelinePersistenceService,
):
    """
    Persistência da Pipeline em JSON.
    """

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:

        self.__settings = settings

        self.__base_path = (
            self.__settings.executions_path
        )

    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Persiste o resultado da Pipeline.
        """

        folder = (
            self.__settings.executions_path /
            self.__build_folder_name(...)
        )

        data = self.__serialize(
            result,
        )

        file = (
            folder /
            "pipeline.json"
        )

        file.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def __create_execution_folder(
        self,
    ) -> Path:
        """
        Cria a pasta da execução.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S",
        )

        folder = (
            self.__base_path /
            f"{timestamp}_{uuid4().hex[:8].upper()}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    def __serialize(
        self,
        result: PipelineResult,
    ) -> dict:
        """
        Serializa o PipelineResult.
        """

        return asdict(
            result,
        )