"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_parser.py
Descrição : Responsável por interpretar a saída do Publish.
--------------------------------------------------------------------
"""

import re
from typing import Any

from app.abstractions.output_parser import (
    OutputParser,
)

from app.models.publish.publish_error import (
    PublishError,
)

from app.models.publish.publish_execution import (
    PublishExecution,
)

from app.models.publish.publish_warning import (
    PublishWarning,
)


class PublishParser(OutputParser):
    """
    Responsável por interpretar a saída do Publish
    executado pelo MSBuild.
    """

    OUTPUT_PATTERN = re.compile(
        r"->\s(?P<directory>.+)"
    )

    ERROR_PATTERN = re.compile(
        r": error (?P<code>[A-Z]+\d+): (?P<message>.+)",
        re.IGNORECASE,
    )

    WARNING_PATTERN = re.compile(
        r": warning (?P<code>[A-Z]+\d+): (?P<message>.+)",
        re.IGNORECASE,
    )

    SUCCESS_PATTERNS = (
        "compilação com êxito.",
        "compilacao com exito.",
        "build succeeded.",
        "build succeeded",
        "publish succeeded.",
        "publish succeeded",
        "publicação concluída.",
        "publicação concluída",
        "publicacao concluida.",
        "publicacao concluida",
    )

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

        self.__parse_request(
            execution=execution,
            publish_context=publish_context,
        )

        self.__parse_output_directory(
            execution=execution,
            output=output,
        )

        self.__parse_errors(
            execution=execution,
            output=output,
        )

        self.__parse_warnings(
            execution=execution,
            output=output,
        )

        execution.summary.total_errors = (
            len(execution.errors)
        )

        execution.summary.total_warnings = (
            len(execution.warnings)
        )

        self.__parse_summary(
            execution=execution,
            output=output,
        )

        return execution

    def __parse_request(
        self,
        execution: PublishExecution,
        publish_context,
    ) -> None:

        request = publish_context.request

        summary = execution.summary

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

    def __parse_summary(
        self,
        execution: PublishExecution,
        output: str,
    ) -> None:

        normalized_output = (
            output.lower()
        )

        has_success_message = any(
            pattern in normalized_output
            for pattern in self.SUCCESS_PATTERNS
        )

        execution.summary.published = (
            has_success_message
            and execution.summary.total_errors == 0
        )

    def __parse_output_directory(
        self,
        execution: PublishExecution,
        output: str,
    ) -> None:

        for line in output.splitlines():

            match = self.OUTPUT_PATTERN.search(
                line,
            )

            if match is None:
                continue

            execution.summary.output_directory = (
                match.group("directory").strip()
            )

    def __parse_errors(
        self,
        execution: PublishExecution,
        output: str,
    ) -> None:

        for line in output.splitlines():

            match = self.ERROR_PATTERN.search(
                line,
            )

            if match is None:
                continue

            execution.errors.append(
                PublishError(
                    code=match.group("code"),
                    message=match.group("message"),
                )
            )

    def __parse_warnings(
        self,
        execution: PublishExecution,
        output: str,
    ) -> None:

        for line in output.splitlines():

            match = self.WARNING_PATTERN.search(
                line,
            )

            if match is None:
                continue

            execution.warnings.append(
                PublishWarning(
                    code=match.group("code"),
                    message=match.group("message"),
                )
            )