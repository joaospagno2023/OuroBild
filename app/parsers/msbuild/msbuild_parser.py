"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_parser.py
Descrição : Responsável por interpretar a saída do MSBuild.
--------------------------------------------------------------------
"""

import re

from app.models.build.build_error import BuildError
from app.models.build.build_execution import BuildExecution
from app.models.build.build_warning import BuildWarning


class MsBuildParser:
    """
    Responsável por interpretar a saída textual do MSBuild.
    """

    ERROR_PATTERN = re.compile(
        r"^(?P<file>.+?)\((?P<line>\d+),(?P<column>\d+)\): error (?P<code>[A-Z]+\d+): (?P<message>.+)$"
    )

    WARNING_PATTERN = re.compile(
        r"^(?P<file>.+?)\((?P<line>\d+),(?P<column>\d+)\): warning (?P<code>[A-Z]+\d+): (?P<message>.+)$"
    )

    SUMMARY_WARNING_PATTERN = re.compile(
        r"^\s*(\d+)\s+Warning\(s\)"
    )

    SUMMARY_ERROR_PATTERN = re.compile(
        r"^\s*(\d+)\s+Error\(s\)"
    )

    def parse(
        self,
        output: str,
    ) -> BuildExecution:
        """
        Interpreta a saída do MSBuild.
        """

        execution = BuildExecution()

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            error = self.__parse_error(line)

            if error is not None:
                execution.errors.append(error)
                continue

            warning = self.__parse_warning(line)

            if warning is not None:
                execution.warnings.append(warning)
                continue

            self.__parse_summary(
                line=line,
                execution=execution,
            )

        execution.summary.total_errors = len(
            execution.errors,
        )

        execution.summary.total_warnings = len(
            execution.warnings,
        )

        execution.summary.build_succeeded = (
            execution.summary.total_errors == 0
        )

        return execution

    def __parse_error(
        self,
        line: str,
    ) -> BuildError | None:

        match = self.ERROR_PATTERN.match(line)

        if match is None:
            return None

        return BuildError(
            file=match.group("file"),
            line=int(match.group("line")),
            column=int(match.group("column")),
            code=match.group("code"),
            message=match.group("message"),
        )

    def __parse_warning(
        self,
        line: str,
    ) -> BuildWarning | None:

        match = self.WARNING_PATTERN.match(line)

        if match is None:
            return None

        return BuildWarning(
            file=match.group("file"),
            line=int(match.group("line")),
            column=int(match.group("column")),
            code=match.group("code"),
            message=match.group("message"),
        )

    def __parse_summary(
        self,
        line: str,
        execution: BuildExecution,
    ) -> None:

        warning = self.SUMMARY_WARNING_PATTERN.match(
            line,
        )

        if warning is not None:

            execution.summary.total_warnings = int(
                warning.group(1),
            )

        error = self.SUMMARY_ERROR_PATTERN.match(
            line,
        )

        if error is not None:

            execution.summary.total_errors = int(
                error.group(1),
            )