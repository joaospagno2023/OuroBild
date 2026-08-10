"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_pipeline_execution_repository.py
Descrição : Implementação do repositório responsável por persistir
             execuções da Pipeline em arquivos JSON.
--------------------------------------------------------------------
"""

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from app.abstractions.pipeline_execution_repository import (
    PipelineExecutionRepository,
)
from app.models.configuration.app_settings import (
    AppSettings,
)
from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class JsonPipelineExecutionRepository(
    PipelineExecutionRepository,
):
    """
    Repositório responsável por persistir execuções
    da Pipeline em arquivos JSON.
    """

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:

        self.__settings = settings

    def save(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Persiste uma execução da Pipeline.
        """

        execution_folder = (
            self.__create_execution_folder()
        )

        pipeline_file = (
            execution_folder /
            "pipeline.json"
        )

        pipeline_file.write_text(
            json.dumps(
                asdict(result),
                indent=4,
                ensure_ascii=False,
                default=str,
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
            self.__settings.executions_path /
            f"{timestamp}_{uuid4().hex[:8].upper()}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder