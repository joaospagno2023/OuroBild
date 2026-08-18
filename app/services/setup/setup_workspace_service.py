"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_workspace_service.py
Descrição : Gerencia o workspace temporário utilizado na preparação
            de projetos Visual Studio Setup.
--------------------------------------------------------------------
"""

import shutil
from pathlib import Path


class SetupWorkspaceService:
    """
    Cria e gerencia uma cópia de trabalho do projeto Setup.

    O arquivo original do TFS nunca é alterado diretamente.
    """

    def create_workspace(
        self,
        setup_project_path: Path,
        workspace_root: Path,
    ) -> Path:
        """
        Cria uma cópia de trabalho do arquivo .vdproj.

        Retorna o caminho do .vdproj temporário.
        """

        if setup_project_path is None:
            raise ValueError(
                "Caminho do projeto Setup não foi informado."
            )

        if workspace_root is None:
            raise ValueError(
                "WorkspaceRoot não foi informado."
            )

        setup_project_path = Path(
            setup_project_path,
        )

        workspace_root = Path(
            workspace_root,
        )

        if not setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup não encontrado: "
                f"{setup_project_path}"
            )

        if not setup_project_path.is_file():
            raise ValueError(
                "Projeto Setup não é um arquivo: "
                f"{setup_project_path}"
            )

        workspace_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            workspace_root
            / setup_project_path.name
        )

        shutil.copy2(
            setup_project_path,
            destination,
        )

        return destination

    def read(
        self,
        workspace_project_path: Path,
    ) -> str:
        """
        Lê o conteúdo do projeto Setup de trabalho.
        """

        if workspace_project_path is None:
            raise ValueError(
                "Caminho do projeto Setup "
                "não foi informado."
            )

        workspace_project_path = Path(
            workspace_project_path,
        )

        if not workspace_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup de trabalho "
                "não encontrado: "
                f"{workspace_project_path}"
            )

        return workspace_project_path.read_text(
            encoding="utf-8",
        )

    def write(
        self,
        workspace_project_path: Path,
        content: str,
    ) -> None:
        """
        Salva o conteúdo no projeto Setup de trabalho.
        """

        if workspace_project_path is None:
            raise ValueError(
                "Caminho do projeto Setup "
                "não foi informado."
            )

        if content is None:
            raise ValueError(
                "Conteúdo do projeto Setup "
                "não foi informado."
            )

        workspace_project_path = Path(
            workspace_project_path,
        )

        workspace_project_path.write_text(
            content,
            encoding="utf-8",
        )

    def cleanup(
        self,
        workspace_root: Path,
    ) -> None:
        """
        Remove o workspace temporário.
        """

        if workspace_root is None:
            raise ValueError(
                "WorkspaceRoot não foi informado."
            )

        workspace_root = Path(
            workspace_root,
        )

        if not workspace_root.exists():
            return

        if not workspace_root.is_dir():
            raise ValueError(
                "WorkspaceRoot não é um diretório: "
                f"{workspace_root}"
            )

        shutil.rmtree(
            workspace_root,
        )