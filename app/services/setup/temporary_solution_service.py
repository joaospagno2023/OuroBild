"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : temporary_solution_service.py
Descrição : Cria uma Solution temporária para geração de Setup.
--------------------------------------------------------------------
"""

import re

from pathlib import Path


class TemporarySolutionService:
    """
    Cria uma cópia temporária da Solution para execução do Setup.

    A Solution original nunca é alterada.

    A Solution temporária:

    - mantém os GUIDs originais;
    - mantém os nomes dos projetos;
    - mantém as configurações da Solution;
    - mantém os demais projetos apontando para os arquivos originais;
    - aponta somente o projeto Setup para o VDPROJ temporário.
    """

    _PROJECT_PATTERN = re.compile(
        r'^\s*'
        r'(Project\("[^"]+"\)\s*=\s*"[^"]+"\s*,\s*)'
        r'"([^"]+)"'
        r'(\s*,\s*"\{[^"]+\}")'
        r'\s*$',
        re.MULTILINE,
    )

    def create(
        self,
        solution_path: Path,
        publish_path: Path,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
    ) -> Path:
        """
        Cria uma Solution temporária.

        A Solution original permanece intacta.
        """

        if solution_path is None:
            raise ValueError(
                "SolutionPath não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath não foi informado."
            )

        if original_setup_project_path is None:
            raise ValueError(
                "OriginalSetupProjectPath "
                "não foi informado."
            )

        if temporary_setup_project_path is None:
            raise ValueError(
                "TemporarySetupProjectPath "
                "não foi informado."
            )

        solution_path = Path(
            solution_path,
        )

        publish_path = Path(
            publish_path,
        )

        original_setup_project_path = Path(
            original_setup_project_path,
        )

        temporary_setup_project_path = Path(
            temporary_setup_project_path,
        )

        if not solution_path.exists():
            raise FileNotFoundError(
                "Solution original não encontrada: "
                f"{solution_path}"
            )

        if not solution_path.is_file():
            raise ValueError(
                "Solution original não é um arquivo: "
                f"{solution_path}"
            )

        if not original_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup original não encontrado: "
                f"{original_setup_project_path}"
            )

        if not temporary_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup temporário não encontrado: "
                f"{temporary_setup_project_path}"
            )

        publish_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = self.__read_solution(
            solution_path,
        )

        content = self.__replace_setup_project(
            content=content,
            solution_directory=solution_path.parent,
            original_setup_project_path=(
                original_setup_project_path
            ),
            temporary_setup_project_path=(
                temporary_setup_project_path
            ),
        )

        temporary_solution_path = (
            publish_path
            / self.__build_solution_name(
                solution_path,
            )
        )

        self.__write_solution(
            temporary_solution_path,
            content,
        )

        return temporary_solution_path

    @staticmethod
    def __read_solution(
        solution_path: Path,
    ) -> str:
        """
        Lê a Solution original.

        Tenta UTF-8 primeiro e utiliza CP1252
        como fallback.
        """

        data = solution_path.read_bytes()

        if data.startswith(
            b"\xef\xbb\xbf"
        ):
            return data.decode(
                "utf-8-sig",
            )

        try:
            return data.decode(
                "utf-8",
            )

        except UnicodeDecodeError:
            return data.decode(
                "cp1252",
            )

    @classmethod
    def __replace_setup_project(
        cls,
        content: str,
        solution_directory: Path,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
    ) -> str:
        """
        Substitui somente a referência do VDPROJ original
        pela referência do VDPROJ temporário.

        Os demais projetos não são alterados.
        """

        original_setup_project_path = (
            original_setup_project_path
            .resolve()
        )

        temporary_setup_project_path = (
            temporary_setup_project_path
            .resolve()
        )

        replaced = False

        lines = content.splitlines(
            keepends=True,
        )

        result = []

        for line in lines:

            line_without_newline = (
                line.rstrip("\r\n")
            )

            match = cls._PROJECT_PATTERN.match(
                line_without_newline,
            )

            if match is None:
                result.append(
                    line,
                )
                continue

            prefix = match.group(1)
            project_path_text = match.group(2)
            suffix = match.group(3)

            project_path = Path(
                project_path_text,
            )

            if project_path.is_absolute():

                resolved_project_path = (
                    project_path.resolve()
                )

            else:

                resolved_project_path = (
                    solution_directory
                    / project_path
                ).resolve()

            if cls.__same_path(
                resolved_project_path,
                original_setup_project_path,
            ):

                newline = (
                    "\r\n"
                    if line.endswith("\r\n")
                    else "\n"
                )

                temporary_project_path = (
                    cls.__solution_path(
                        temporary_setup_project_path,
                    )
                )

                result.append(
                    prefix
                    + '"'
                    + temporary_project_path
                    + '"'
                    + suffix
                    + newline
                )

                replaced = True

                continue

            result.append(
                line,
            )

        if not replaced:
            return content

        return "".join(
            result,
        )

    @staticmethod
    def __same_path(
        first: Path,
        second: Path,
    ) -> bool:
        """
        Compara dois caminhos normalizados.
        """

        return (
            first.resolve()
            == second.resolve()
        )

    @staticmethod
    def __solution_path(
        path: Path,
    ) -> str:
        """
        Converte um caminho para o formato utilizado
        pelo arquivo .sln.

        Mantém o caminho absoluto para que a Solution
        temporária consiga localizar o projeto original
        independentemente de onde ela esteja armazenada.
        """

        return str(
            path.resolve(),
        ).replace(
            "\\",
            "/",
        )

    @staticmethod
    def __build_solution_name(
        solution_path: Path,
    ) -> str:
        """
        Gera o nome da Solution temporária.
        """

        return (
            f"{solution_path.stem}"
            ".OuroBuild.sln"
        )

    @staticmethod
    def __write_solution(
        solution_path: Path,
        content: str,
    ) -> None:
        """
        Grava a Solution temporária.
        """

        solution_path.write_text(
            content,
            encoding="utf-8",
            newline="",
        )