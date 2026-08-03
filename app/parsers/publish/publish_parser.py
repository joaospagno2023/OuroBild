"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_parser.py
Descrição : Responsável por interpretar a saída do dotnet publish.
--------------------------------------------------------------------
"""

import re
from typing import Any

from app.abstractions.output_parser import OutputParser
from app.models.publish.publish_error import PublishError
from app.models.publish.publish_execution import (
    PublishExecution,
)
from app.models.publish.publish_warning import (
    PublishWarning,
)


class PublishParser(OutputParser):
    """
    Responsável por interpretar a saída do dotnet publish.
    """

    OUTPUT_PATTERN = re.compile(
        r"->\s(?P<directory>.+)"
    )

    ERROR_PATTERN = re.compile(
        r": error (?P<code>[A-Z]+\d+): (?P<message>.+)"
    )

    WARNING_PATTERN = re.compile(
        r": warning (?P<code>[A-Z]+\d+): (?P<message>.+)"
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
            execution,
            publish_context,
        )

        self.__parse_summary(
            execution,
            output,
        )

        self.__parse_output_directory(
            execution,
            output,
        )

        self.__parse_errors(
            execution,
            output,
        )

        self.__parse_warnings(
            execution,
            output,
        )

        execution.summary.total_errors = (
            len(execution.errors)
        )

        execution.summary.total_warnings = (
            len(execution.warnings)
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

        output = output.lower()

        execution.summary.published = (

            "publish succeeded" in output

            or

            "publicação concluída" in output
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