"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_artifact_cleanup_service.py
Descrição : Remove artefatos desnecessários do workspace do Build.
--------------------------------------------------------------------
"""

import shutil

from pathlib import Path

from app.models.cleanup.cleanup_result import (
    CleanupResult,
)

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupRule,
    CleanupTarget,
)


class BuildArtifactCleanupService:
    """
    Executa a limpeza dos artefatos do Build.
    """

    def __init__(
        self,
        rules: list[CleanupRule],
    ) -> None:

        if rules is None:
            raise ValueError(
                "Regras de Cleanup não foram informadas."
            )

        self.__rules = list(
            rules
        )

    def execute(
        self,
        workspace_path: Path,
        project_id: str | None = None,
        dry_run: bool = False,
    ) -> CleanupResult:
        """
        Executa a limpeza do workspace.
        """

        if workspace_path is None:
            raise ValueError(
                "Workspace do Build não foi informado."
            )

        workspace_path = Path(
            workspace_path,
        )

        if not workspace_path.exists():
            raise ValueError(
                "Workspace do Build não existe."
            )

        if not workspace_path.is_dir():
            raise ValueError(
                "Workspace do Build não é um diretório."
            )

        result = CleanupResult(
            workspace_path=workspace_path,
            dry_run=dry_run,
        )

        self.__process_files(
            workspace_path=workspace_path,
            project_id=project_id,
            result=result,
            dry_run=dry_run,
        )

        self.__process_directories(
            workspace_path=workspace_path,
            project_id=project_id,
            result=result,
            dry_run=dry_run,
        )

        return result

    def __process_files(
        self,
        workspace_path: Path,
        project_id: str | None,
        result: CleanupResult,
        dry_run: bool,
    ) -> None:
        """
        Processa os arquivos.

        As regras de arquivo são independentes das
        regras de diretório.
        """

        files = [
            path
            for path in workspace_path.rglob("*")
            if path.is_file()
        ]

        result.files_analyzed = len(
            files
        )

        for file_path in files:

            rule = self.__find_rule(
                target=CleanupTarget.FILE,
                path=file_path,
                project_id=project_id,
            )

            if rule is None:

                result.files_preserved.append(
                    file_path
                )

                continue

            if (
                rule.action
                == CleanupAction.PRESERVE
            ):

                result.files_preserved.append(
                    file_path
                )

                continue

            if (
                rule.action
                == CleanupAction.REMOVE
            ):

                result.files_removed.append(
                    file_path
                )

                if dry_run:
                    continue

                self.__remove_file(
                    file_path=file_path,
                    result=result,
                )

    def __process_directories(
        self,
        workspace_path: Path,
        project_id: str | None,
        result: CleanupResult,
        dry_run: bool,
    ) -> None:
        """
        Processa os diretórios.

        Diretórios com regra REMOVE são removidos
        recursivamente.

        Diretórios com regra PRESERVE permanecem.
        """

        directories = [
            path
            for path in workspace_path.rglob("*")
            if path.is_dir()
        ]

        result.directories_analyzed = len(
            directories
        )

        directories = sorted(
            directories,
            key=lambda path: len(
                path.parts
            ),
            reverse=True,
        )

        for directory_path in directories:

            if not directory_path.exists():
                continue

            rule = self.__find_rule(
                target=CleanupTarget.DIRECTORY,
                path=directory_path,
                project_id=project_id,
            )

            if rule is None:

                result.directories_preserved.append(
                    directory_path
                )

                continue

            if (
                rule.action
                == CleanupAction.PRESERVE
            ):

                result.directories_preserved.append(
                    directory_path
                )

                continue

            if (
                rule.action
                == CleanupAction.REMOVE
            ):

                result.directories_removed.append(
                    directory_path
                )

                if dry_run:
                    continue

                self.__remove_directory(
                    directory_path=directory_path,
                    result=result,
                )

    def __find_rule(
        self,
        target: CleanupTarget,
        path: Path,
        project_id: str | None,
    ) -> CleanupRule | None:
        """
        Localiza a regra aplicável.

        Prioridade:

        1. Regra específica do projeto.
        2. Regra global.
        """

        global_rule = None

        for rule in self.__rules:

            if rule.target != target:
                continue

            if not self.__matches_rule(
                rule=rule,
                path=path,
            ):
                continue

            if (
                rule.project_id is not None
                and rule.project_id == project_id
            ):

                return rule

            if rule.project_id is None:

                global_rule = rule

        return global_rule

    @staticmethod
    def __matches_rule(
        rule: CleanupRule,
        path: Path,
    ) -> bool:
        """
        Verifica se o caminho corresponde à regra.
        """

        if rule.pattern == "*":
            return True

        if rule.recursive:

            return path.match(
                rule.pattern,
            )

        return (
            path.name.lower()
            == rule.pattern.lower()
        )

    @staticmethod
    def __remove_file(
        file_path: Path,
        result: CleanupResult,
    ) -> None:
        """
        Remove um arquivo.
        """

        try:

            file_path.unlink()

        except OSError as error:

            result.errors.append(
                (
                    "Não foi possível remover "
                    f"o arquivo '{file_path}': "
                    f"{error}"
                )
            )

    @staticmethod
    def __remove_directory(
        directory_path: Path,
        result: CleanupResult,
    ) -> None:
        """
        Remove um diretório recursivamente.
        """

        try:

            shutil.rmtree(
                directory_path,
            )

        except OSError as error:

            result.errors.append(
                (
                    "Não foi possível remover "
                    f"o diretório '{directory_path}': "
                    f"{error}"
                )
            )