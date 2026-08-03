"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_parser.py
Descrição : Responsável por interpretar a saída do dotnet publish.
--------------------------------------------------------------------
"""

from typing import Any

from app.abstractions.output_parser import OutputParser
from app.models.publish.publish_execution import PublishExecution


class PublishParser(OutputParser):
    """
    Responsável por interpretar a saída do dotnet publish.
    """

    def parse(
        self,
        output: str,
        context: Any | None = None,
    ) -> PublishExecution:

        execution = PublishExecution()

        if context is None:
            return execution

        publish_context = (
            context.variables["publish_context"]
        )

        request = publish_context.request

        summary = execution.summary

        #
        # Informações da requisição
        #

        summary.configuration = (
            request.configuration
        )

        summary.framework = (
            request.framework or ""
        )

        summary.runtime = (
            request.runtime or ""
        )

        summary.output_directory = (
            request.output_directory or ""
        )

        summary.publish_profile = (
            request.publish_profile or ""
        )

        summary.self_contained = (
            request.self_contained
        )

        summary.single_file = (
            request.single_file
        )

        summary.ready_to_run = (
            request.ready_to_run
        )

        summary.trimmed = (
            request.trimmed
        )

        #
        # Resultado da execução
        #

        output_lower = output.lower()

        summary.published = (
            "publish succeeded" in output_lower
            or "publicação concluída" in output_lower
        )

        return execution