"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_workspace_service.py
Descrição : Gerencia o workspace temporário utilizado pelo
            Advanced Installer durante a geração do Setup.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
import shutil
from pathlib import Path


@dataclass(frozen=True)
class AdvancedInstallerWorkspacePaths:
    """
    Representa os caminhos utilizados por uma execução do
    Advanced Installer.
    """

    project_id: str
    workspace_path: Path
    aip_path: Path
    prerequisites_path: Path
    publish_path: Path


class AdvancedInstallerWorkspaceService:
    """
    Gerencia o workspace temporário utilizado pelo
    Advanced Installer.

    O workspace contém somente os arquivos necessários para
    uma execução específica do Setup.

    Estrutura:

        workspace_root
            └── project_id
                ├── AIP
                │   └── <arquivo>.aip
                ├── Prerequisites
                │   └── <arquivos>
                └── Release
                    └── <arquivos>

    Os arquivos originais nunca são alterados diretamente.
    """

    def __init__(
        self,
        workspace_root: Path,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if workspace_root is None:
            raise ValueError(
                "WorkspaceRoot não foi informado."
            )

        self.__workspace_root = Path(
            workspace_root,
        )

    def create(
        self,
        project_id: str,
    ) -> Path:
        """
        Cria um workspace limpo para o projeto.

        Se já existir um workspace anterior para o projeto,
        ele será removido antes da criação.

        Returns:
            Caminho do workspace do projeto.
        """

        project_id = self.__validate_project_id(
            project_id,
        )

        if self.__workspace_root.exists() and not self.__workspace_root.is_dir():
            raise ValueError(
                "O workspace do projeto não é um diretório: "
                f"{self.__workspace_root}"
            )

        project_workspace = (
            self.__workspace_root
            / project_id
        )

        if project_workspace.exists():

            if not project_workspace.is_dir():
                raise ValueError(
                    "O workspace do projeto não é um "
                    "diretório: "
                    f"{project_workspace}"
                )

            shutil.rmtree(
                project_workspace,
            )

        project_workspace.mkdir(
            parents=True,
            exist_ok=True,
        )

        return project_workspace

    def prepare(
        self,
        project_id: str,
        aip_path: Path,
        prerequisites_path: Path,
        publish_path: Path,
    ) -> AdvancedInstallerWorkspacePaths:
        """
        Cria e prepara o workspace completo de uma execução.

        São copiadas três fontes para o workspace:

        - AIP para <workspace>/AIP;
        - Prerequisites para <workspace>/Prerequisites;
        - Release/Publish para <workspace>/Release.

        As fontes originais permanecem intactas.
        """

        project_id = self.__validate_project_id(
            project_id,
        )

        aip_source = self.__validate_file(
            aip_path,
            "Arquivo AIP",
        )

        prerequisites_source = self.__validate_directory(
            prerequisites_path,
            "Diretório Prerequisites",
        )

        publish_source = self.__validate_directory(
            publish_path,
            "Diretório Release",
        )

        workspace_path = self.create(
            project_id=project_id,
        )

        workspace_aip_directory = (
            workspace_path
            / "AIP"
        )

        workspace_prerequisites_path = (
            workspace_aip_directory
            / "Prerequisites"
        )

        workspace_publish_path = (
            workspace_path
            / "Release"
        )

        workspace_aip_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            aip_source,
            workspace_aip_directory / aip_source.name,
        )

        shutil.copytree(
            prerequisites_source,
            workspace_prerequisites_path,
            dirs_exist_ok=True,
        )

        shutil.copytree(
            publish_source,
            workspace_publish_path,
            dirs_exist_ok=True,
        )

        workspace_aip_path = (
            workspace_aip_directory
            / aip_source.name
        )

        return AdvancedInstallerWorkspacePaths(
            project_id=project_id,
            workspace_path=workspace_path,
            aip_path=workspace_aip_path,
            prerequisites_path=workspace_prerequisites_path,
            publish_path=workspace_publish_path,
        )

    def cleanup(
        self,
        workspace_path: Path,
    ) -> None:
        """
        Remove o workspace de uma execução.
        """

        if workspace_path is None:
            raise ValueError(
                "WorkspacePath não foi informado."
            )

        workspace_path = Path(
            workspace_path,
        )

        if not workspace_path.exists():
            return

        if not workspace_path.is_dir():
            raise ValueError(
                "WorkspacePath não é um diretório: "
                f"{workspace_path}"
            )

        shutil.rmtree(
            workspace_path,
        )

    def cleanup_root(self) -> None:
        """
        Remove todos os workspaces existentes.

        Utilizado para garantir que uma execução comece
        sem resíduos de execuções anteriores.
        """

        if not self.__workspace_root.exists():
            return

        if not self.__workspace_root.is_dir():
            raise ValueError(
                "WorkspaceRoot não é um diretório: "
                f"{self.__workspace_root}"
            )

        for item in self.__workspace_root.iterdir():

            if item.is_dir():
                shutil.rmtree(
                    item,
                )
                continue

            item.unlink()

    @staticmethod
    def __validate_project_id(
        project_id: str,
    ) -> str:
        """
        Valida e normaliza o identificador do projeto.

        O ProjectId é um nome de diretório simples e não pode
        carregar caminho relativo ou absoluto.
        """

        if not project_id or not project_id.strip():
            raise ValueError(
                "ProjectId não foi informado."
            )

        project_id = project_id.strip()

        if project_id in {".", ".."}:
            raise ValueError(
                "ProjectId inválido."
            )

        if "/" in project_id or "\\" in project_id:
            raise ValueError(
                "ProjectId não pode conter separadores de diretório."
            )

        if Path(project_id).is_absolute():
            raise ValueError(
                "ProjectId não pode ser um caminho absoluto."
            )

        if Path(project_id).name != project_id:
            raise ValueError(
                "ProjectId deve representar somente o nome do projeto."
            )

        return project_id

    @staticmethod
    def __validate_file(
        path: Path,
        description: str,
    ) -> Path:
        """
        Valida um arquivo de origem.
        """

        if path is None:
            raise ValueError(
                f"{description} não foi informado."
            )

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{description} não encontrado: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"{description} não é um arquivo: {path}"
            )

        return path

    @staticmethod
    def __validate_directory(
        path: Path,
        description: str,
    ) -> Path:
        """
        Valida um diretório de origem.
        """

        if path is None:
            raise ValueError(
                f"{description} não foi informado."
            )

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"{description} não encontrado: {path}"
            )

        if not path.is_dir():
            raise ValueError(
                f"{description} não é um diretório: {path}"
            )

        return path
