"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_workspace_service.py
Descrição : Cria uma cópia de trabalho do arquivo de Setup.
--------------------------------------------------------------------
"""

from pathlib import Path
import shutil


class SetupWorkspaceService:
    """
    Responsável por criar o arquivo de Setup de trabalho.

    O arquivo original do TFS nunca é alterado.
    """

    def __init__(self) -> None:
        """
        Inicializa o serviço.
        """

    def create(
        self,
        setup_project_path: Path,
        setup_output_path: Path,
    ) -> Path:
        """
        Cria uma cópia de trabalho do arquivo de Setup.

        Parameters
        ----------
        setup_project_path:
            Caminho do arquivo .vdproj original.

        setup_output_path:
            Diretório onde será criada a cópia de trabalho.

        Returns
        -------
        Path
            Caminho do arquivo .vdproj de trabalho.
        """

        if setup_project_path is None:
            raise ValueError(
                "setup_project_path não foi informado."
            )

        if setup_output_path is None:
            raise ValueError(
                "setup_output_path não foi informado."
            )

        setup_project_path = Path(
            setup_project_path
        )

        setup_output_path = Path(
            setup_output_path
        )

        if not setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto de Setup não encontrado: "
                f"{setup_project_path}"
            )

        if not setup_project_path.is_file():
            raise ValueError(
                "O caminho informado para o Projeto de Setup "
                "não é um arquivo: "
                f"{setup_project_path}"
            )

        setup_output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        working_setup_path = (
            setup_output_path
            / setup_project_path.name
        )

        shutil.copy2(
            setup_project_path,
            working_setup_path,
        )

        return working_setup_path