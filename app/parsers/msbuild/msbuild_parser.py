"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_parser.py
Descrição : Responsável por interpretar a saída do MSBuild.
--------------------------------------------------------------------
"""

import re
from pathlib import Path

from app.models.build.build_error import BuildError
from app.models.build.build_execution import BuildExecution
from app.models.build.build_warning import BuildWarning
from typing import Any

from app.abstractions.output_parser import OutputParser


class MsBuildParser(OutputParser):
    """
    Responsável por interpretar a saída textual do MSBuild.
    """

    ERROR_PATTERN = re.compile(
        r"^(?P<file>.+?)"
        r"\((?P<line>\d+),(?P<column>\d+)\): "
        r"error(?: (?P<code>[A-Z]+\d+))?: "
        r"(?P<message>.+)$",
        re.IGNORECASE,
    )

    WARNING_PATTERN = re.compile(
        r"^(?P<file>.+?)"
        r"\((?P<line>\d+),(?P<column>\d+)\): "
        r"warning(?: (?P<code>[A-Z]+\d+))?: "
        r"(?P<message>.+)$",
        re.IGNORECASE,
    )

    PROJECT_PATTERN = re.compile(
        r"\[(?P<project>.+?\.csproj)\]$"
    )

    def parse(
        self,
        output: str,
        context: Any | None = None,
    ) -> BuildExecution:
        """
        Interpreta a saída do MSBuild.
        """

        execution = BuildExecution()

        error_keys: set[tuple] = set()
        warning_keys: set[tuple] = set()

        for line in output.splitlines():

            line = line.strip()

            

            if not line:
                continue

            error = self.__parse_error(line)

            if error is not None:

                key = (
                    error.file,
                    error.line,
                    error.column,
                    error.code,
                )

                if key not in error_keys:

                    error_keys.add(key)

                    execution.errors.append(error)

                continue

            warning = self.__parse_warning(line)

            if warning is not None:

                key = (
                    warning.file,
                    warning.line,
                    warning.column,
                    warning.code,
                )

                if key not in warning_keys:

                    warning_keys.add(key)

                    execution.warnings.append(warning)

        self.__build_summary(
            execution,
        )

        return execution

    def __parse_error(
        self,
        line: str,
    ) -> BuildError | None:

        match = self.ERROR_PATTERN.match(
            line,
        )
        
        if match is None:
            return None

        project = self.__extract_project(
            match.group("message"),
        )

        return BuildError(
            project=project,
            file=match.group("file"),
            line=int(match.group("line")),
            column=int(match.group("column")),
            code=match.group("code") or "",
            message=match.group("message"),
        )

    def __parse_warning(
        self,
        line: str,
    ) -> BuildWarning | None:

        match = self.WARNING_PATTERN.match(
            line,
        )

        if match is None:
            return None

        project = self.__extract_project(
            match.group("message"),
        )

        return BuildWarning(
            project=project,
            file=match.group("file"),
            line=int(match.group("line")),
            column=int(match.group("column")),
            code=match.group("code"),
            message=match.group("message"),
        )

    def __extract_project(
        self,
        message: str,
    ) -> str:
        """
        Extrai o nome do projeto (.csproj) presente
        ao final da mensagem do MSBuild.
        """

        match = self.PROJECT_PATTERN.search(
            message,
        )

        if match is None:
            return ""

        project_file = Path(
            match.group("project"),
        )

        return project_file.stem

    def __build_summary(
        self,
        execution: BuildExecution,
    ) -> None:
        """
        Atualiza o resumo da execução.
        """

        execution.summary.total_errors = len(
            execution.errors,
        )

        execution.summary.total_warnings = len(
            execution.warnings,
        )

        execution.summary.build_succeeded = (
            execution.summary.total_errors == 0
        )