"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_log_service.py
Descrição : Serviço responsável por persistir os logs de execução
            da Engine.
--------------------------------------------------------------------
"""

import json

from pathlib import Path

from app.models.execution.execution_session import (
    ExecutionLog,
)


class ExecutionSessionService:
    """
    Responsável por persistir os logs de execução.
    """

    def __init__(
        self,
        logs_root: Path,
    ) -> None:
        """
        Inicializa o serviço.
        """

        self.__logs_root = (
            logs_root /
            "executions"
        )

    def save(
        self,
        execution: ExecutionLog,
        output: str,
    ) -> Path:
        """
        Salva uma execução.
        """

        folder = (
            self.__logs_root /
            execution.category /
            f"{execution.started_at:%Y%m%d_%H%M%S}_{execution.execution_id}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        execution.execution_folder = folder

        metadata_file = (
            folder /
            execution.metadata_file
        )

        output_file = (
            folder /
            execution.output_file
        )

        metadata = execution.model_dump(
            mode="json",
        )

        metadata["execution_folder"] = str(
            folder,
        )

        metadata_file.write_text(

            json.dumps(

                metadata,

                indent=4,

                ensure_ascii=False,

            ),

            encoding="utf-8",

        )

        output_file.write_text(

            output,

            encoding="utf-8",

        )

        return folder