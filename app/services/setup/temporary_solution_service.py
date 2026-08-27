"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : temporary_solution_service.py
Descrição : Cria uma Solution temporária para geração do Setup.
--------------------------------------------------------------------
"""

import re

from pathlib import Path


class TemporarySolutionService:
    """
    Cria uma cópia temporária da Solution para geração do Setup.

    A Solution original nunca é alterada.

    A cópia temporária:

        - recebe o sufixo .OuroBuild;
        - referencia o VDPROJ temporário;
        - mantém os demais projetos;
        - mantém os GUIDs originais;
        - remove os bindings de Source Control/TFS.
    """

    def create(
        self,
        solution_path: Path,
        publish_path: Path,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
    ) -> Path:
        """
        Cria uma Solution temporária.

        Args:
            solution_path:
                Caminho da Solution original.

            publish_path:
                Diretório onde a Solution temporária será criada.

            original_setup_project_path:
                Caminho do VDPROJ original referenciado
                pela Solution.

            temporary_setup_project_path:
                Caminho do VDPROJ temporário que deverá
                ser referenciado pela nova Solution.

        Returns:
            Caminho da Solution temporária.
        """

        if solution_path is None:

            raise ValueError(
                "SolutionPath "
                "não foi informado."
            )

        if publish_path is None:

            raise ValueError(
                "PublishPath "
                "não foi informado."
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

        #
        # ------------------------------------------------------------
        # Validação da Solution original.
        # ------------------------------------------------------------
        #

        if not solution_path.exists():

            raise FileNotFoundError(
                "Solution original "
                "não encontrada: "
                f"{solution_path}"
            )

        if not solution_path.is_file():

            raise ValueError(
                "Solution original "
                "não é um arquivo: "
                f"{solution_path}"
            )

        #
        # ------------------------------------------------------------
        # Validação do projeto Setup temporário.
        # ------------------------------------------------------------
        #

        if not temporary_setup_project_path.exists():

            raise FileNotFoundError(
                "Projeto Setup temporário "
                "não encontrado: "
                f"{temporary_setup_project_path}"
            )

        if not temporary_setup_project_path.is_file():

            raise ValueError(
                "Projeto Setup temporário "
                "não é um arquivo: "
                f"{temporary_setup_project_path}"
            )

        #
        # ------------------------------------------------------------
        # Criação do diretório de publicação.
        # ------------------------------------------------------------
        #

        publish_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        #
        # ------------------------------------------------------------
        # Leitura da Solution original.
        # ------------------------------------------------------------
        #

        content = solution_path.read_text(
            encoding="utf-8",
        )

        #
        # ------------------------------------------------------------
        # Remove bindings de Source Control.
        # ------------------------------------------------------------
        #

        content = (
            self.__remove_source_control_bindings(
                content,
            )
        )

        #
        # ------------------------------------------------------------
        # Substitui somente a referência do projeto Setup.
        # ------------------------------------------------------------
        #

        content = (
            self.__replace_setup_project_reference(
                content=content,
                original_setup_project_path=(
                    original_setup_project_path
                ),
                temporary_setup_project_path=(
                    temporary_setup_project_path
                ),
            )
        )

        #
        # ------------------------------------------------------------
        # Nome da Solution temporária.
        # ------------------------------------------------------------
        #

        temporary_solution_name = (
            solution_path.stem
            + ".OuroBuild"
            + solution_path.suffix
        )

        temporary_solution_path = (
            publish_path
            / temporary_solution_name
        )

        #
        # ------------------------------------------------------------
        # Grava somente a cópia.
        # ------------------------------------------------------------
        #

        temporary_solution_path.write_text(
            content,
            encoding="utf-8",
        )

        return temporary_solution_path

    @staticmethod
    def __replace_setup_project_reference(
        content: str,
        original_setup_project_path: Path,
        temporary_setup_project_path: Path,
    ) -> str:
        """
        Substitui a referência do VDPROJ original
        pela referência do VDPROJ temporário.

        Somente o caminho do projeto é alterado.
        O nome lógico e o GUID permanecem intactos.
        """

        original_relative_path = (
            TemporarySolutionService
            .__normalize_solution_path(
                original_setup_project_path,
            )
        )

        temporary_relative_path = (
            TemporarySolutionService
            .__normalize_solution_path(
                temporary_setup_project_path,
            )
        )

        #
        # Normalização dos caminhos para comparação.
        #

        original_file_name = (
            original_setup_project_path.name
        )

        temporary_file_name = (
            temporary_setup_project_path.name
        )

        #
        # Primeiro tenta substituir o caminho completo.
        #

        if original_relative_path in content:

            return content.replace(
                original_relative_path,
                temporary_relative_path,
                1,
            )

        #
        # Caso a Solution contenha somente o caminho
        # relativo a partir da raiz da Solution, utiliza
        # o nome do arquivo como fallback.
        #
        # Isso mantém a alteração restrita à referência
        # do projeto Setup.
        #

        pattern = re.compile(
            rf'(?P<prefix>"[^"]*",\s*"[^"]*'
            rf'\\)?'
            rf'{re.escape(original_file_name)}'
            rf'(?P<suffix>"\s*,\s*"\{{[^"]+\}}")',
            re.IGNORECASE,
        )

        match = pattern.search(
            content,
        )

        if match:

            start = match.start()

            end = match.end()

            matched = content[
                start:end
            ]

            replaced = matched.replace(
                original_file_name,
                temporary_file_name,
            )

            return (
                content[:start]
                + replaced
                + content[end:]
            )

        raise ValueError(
            "Referência do projeto Setup original "
            "não foi encontrada na Solution: "
            f"{original_setup_project_path}"
        )

    @staticmethod
    def __normalize_solution_path(
        path: Path,
    ) -> str:
        """
        Converte um caminho para o formato utilizado
        dentro de arquivos .sln.
        """

        return str(
            path
        ).replace(
            "/",
            "\\",
        )

    @staticmethod
    def __remove_source_control_bindings(
        content: str,
    ) -> str:
        """
        Remove completamente o GlobalSection(SourceCodeControl).

        A remoção contempla também qualquer Scc* eventualmente
        presente fora da seção.
        """

        #
        # Remove a seção completa:
        #
        # GlobalSection(SourceCodeControl) = preSolution
        # ...
        # EndGlobalSection
        #

        content = re.sub(
            r'^[ \t]*GlobalSection\(SourceCodeControl\)'
            r'[^\r\n]*\r?\n'
            r'.*?'
            r'^[ \t]*EndGlobalSection[ \t]*'
            r'(?:\r?\n|$)',
            "",
            content,
            flags=(
                re.MULTILINE
                | re.DOTALL
            ),
        )

        #
        # Remove propriedades Scc* que eventualmente
        # tenham permanecido fora da seção.
        #

        content = re.sub(
            r'^[ \t]*Scc[^\r\n]*'
            r'(?:\r?\n|$)',
            "",
            content,
            flags=re.MULTILINE,
        )

        return content