"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : visual_studio_setup_preparer.py
Descrição : Cria uma Solution temporária para utilização do
            projeto Visual Studio Setup preparado.
--------------------------------------------------------------------
"""

import re
import shutil
from pathlib import Path


class VisualStudioSetupPreparer:
    """
    Prepara uma Solution temporária para executar um projeto
    Visual Studio Setup (.vdproj) preparado.

    A Solution original nunca é alterada.

    A cópia da Solution permanece no mesmo diretório da Solution
    original para preservar os caminhos relativos dos demais
    projetos.

    Somente a referência do projeto .vdproj é substituída para
    apontar para o projeto preparado.
    """

    def prepare(
        self,
        solution_path: Path,
        original_setup_project_path: Path,
        prepared_setup_project_path: Path,
        workspace_root: Path,
    ) -> Path:
        """
        Cria uma Solution temporária apontando para o VDPROJ
        preparado.

        Args:
            solution_path:
                Caminho da Solution original.

            original_setup_project_path:
                Caminho do VDPROJ original.

            prepared_setup_project_path:
                Caminho do VDPROJ preparado.

            workspace_root:
                Diretório onde será criada a Solution temporária.

        Returns:
            Caminho da Solution temporária.
        """

        if solution_path is None:
            raise ValueError(
                "SolutionPath não foi informado."
            )

        if original_setup_project_path is None:
            raise ValueError(
                "OriginalSetupProjectPath "
                "não foi informado."
            )

        if prepared_setup_project_path is None:
            raise ValueError(
                "PreparedSetupProjectPath "
                "não foi informado."
            )

        if workspace_root is None:
            raise ValueError(
                "WorkspaceRoot não foi informado."
            )

        solution_path = Path(
            solution_path,
        )

        original_setup_project_path = Path(
            original_setup_project_path,
        )

        prepared_setup_project_path = Path(
            prepared_setup_project_path,
        )

        workspace_root = Path(
            workspace_root,
        )

        if not solution_path.exists():
            raise FileNotFoundError(
                "Solution não encontrada: "
                f"{solution_path}"
            )

        if not solution_path.is_file():
            raise ValueError(
                "Solution não é um arquivo: "
                f"{solution_path}"
            )

        if not original_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup original "
                "não encontrado: "
                f"{original_setup_project_path}"
            )

        if not prepared_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup preparado "
                "não encontrado: "
                f"{prepared_setup_project_path}"
            )

        workspace_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = solution_path.read_text(
            encoding="utf-8",
        )

        original_reference = (
            self.__build_solution_reference(
                solution_path=solution_path,
                setup_project_path=(
                    original_setup_project_path
                ),
            )
        )

        prepared_reference = (
            self.__build_solution_reference(
                solution_path=solution_path,
                setup_project_path=(
                    prepared_setup_project_path
                ),
            )
        )

        if original_reference not in content:
            raise ValueError(
                "O projeto Setup original "
                "não foi encontrado na Solution: "
                f"{original_reference}"
            )

        content = content.replace(
            original_reference,
            prepared_reference,
            1,
        )

        prepared_solution_path = (
            workspace_root
            / solution_path.name
        )

        prepared_solution_path.write_text(
            content,
            encoding="utf-8",
        )

        return prepared_solution_path

    @staticmethod
    def __build_solution_reference(
        solution_path: Path,
        setup_project_path: Path,
    ) -> str:
        """
        Monta o caminho do projeto utilizado pela Solution.

        Como o caminho pode ser absoluto, usamos uma forma
        compatível com o formato textual da .sln.
        """

        try:
            relative_path = (
                setup_project_path
                .relative_to(
                    solution_path.parent
                )
            )

            path = str(
                relative_path
            )

        except ValueError:

            path = str(
                setup_project_path
            )

        return path.replace(
            "/",
            "\\",
        )