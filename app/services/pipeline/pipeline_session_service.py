"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : pipeline_session_service.py
Descrição : Responsável por criar e gerenciar a estrutura física de
            uma execução da Pipeline.
--------------------------------------------------------------------
"""

import json

from pathlib import Path

from app.models.pipeline.pipeline_result import (
    PipelineResult,
)


class PipelineSessionService:
    """
    Responsável por criar a estrutura de uma
    sessão de Pipeline.
    """

    def __init__(
        self,
        base_path: Path,
    ) -> None:
        """
        Inicializa o serviço.
        """

        self.__base_path = (
            base_path /
            "executions"
        )

    def create(
        self,
        result: PipelineResult,
    ) -> Path:
        """
        Cria a estrutura física da sessão.
        """

        folder = (
            self.__base_path /
            self.__build_folder_name(
                result,
            )
        )

        #
        # Estrutura
        #

        (folder / "logs").mkdir(
            parents=True,
            exist_ok=True,
        )

        (folder / "artifacts").mkdir(
            exist_ok=True,
        )

        (folder / "reports").mkdir(
            exist_ok=True,
        )

        result.output_folder = folder

        #
        # Salva session.json
        #

        session_file = (
            folder /
            "session.json"
        )

        session = {

            "session_id":
                result.session_id,

            "started_at":
                (
                    result.started_at.isoformat()
                    if result.started_at
                    else None
                ),

            "finished_at":
                (
                    result.finished_at.isoformat()
                    if result.finished_at
                    else None
                ),

            "elapsed_seconds":
                result.elapsed_seconds,

            "success":
                result.success,

            "message":
                result.message,

            "failed_step":
                result.failed_step,

        }

        session_file.write_text(

            json.dumps(

                session,

                indent=4,

                ensure_ascii=False,

            ),

            encoding="utf-8",

        )

        return folder

    def __build_folder_name(
        self,
        result: PipelineResult,
    ) -> str:
        """
        Gera o nome da pasta da sessão.
        """

        timestamp = (
            result.started_at.strftime(
                "%Y%m%d_%H%M%S",
            )
            if result.started_at
            else "unknown"
        )

        return (
            f"{timestamp}_{result.session_id}"
        )