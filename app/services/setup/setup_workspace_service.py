"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_workspace_service.py
Descrição : Gerencia o workspace temporário utilizado na preparação
            de projetos Visual Studio Setup.
--------------------------------------------------------------------
"""

import os
import shutil
import stat

from pathlib import Path


class SetupWorkspaceService:
    """
    Cria e gerencia uma cópia de trabalho do projeto Setup.

    O arquivo original do TFS/TFVC pode estar marcado como
    ReadOnly. Durante o processo controlado de geração do Setup,
    o arquivo original pode ser substituído temporariamente pelo
    arquivo preparado.

    Ao final da operação, o arquivo original é restaurado e seu
    estado de ReadOnly é preservado.
    """

    def create_workspace(
        self,
        setup_project_path: Path,
        workspace_root: Path,
    ) -> Path:
        """
        Cria uma cópia de trabalho do arquivo .vdproj.

        A cópia de trabalho NÃO preserva o atributo ReadOnly
        do arquivo original, pois ela precisa ser modificada
        durante a preparação do Setup.

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

        #
        # copyfile() é utilizado em vez de copy2()
        # para NÃO copiar os atributos do arquivo original.
        #
        # Isso é importante quando o arquivo do TFS/TFVC
        # está marcado como ReadOnly.
        #

        shutil.copyfile(
            setup_project_path,
            destination,
        )

        #
        # Garante que a cópia de trabalho seja gravável.
        #

        self.__make_writable(
            destination,
        )

        return destination

    def backup_original(
        self,
        setup_project_path: Path,
        workspace_root: Path,
    ) -> Path:
        """
        Cria um backup do .vdproj original.

        O backup fica dentro do workspace temporário.

        Diferentemente da cópia de trabalho, o backup preserva
        os atributos do arquivo original, porque esses atributos
        serão utilizados posteriormente para restaurar o estado
        original do arquivo.
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
                "Projeto Setup original não encontrado: "
                f"{setup_project_path}"
            )

        if not setup_project_path.is_file():
            raise ValueError(
                "Projeto Setup original não é um arquivo: "
                f"{setup_project_path}"
            )

        backup_root = (
            workspace_root
            / ".backup"
        )

        backup_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_path = (
            backup_root
            / setup_project_path.name
        )

        #
        # copy2() preserva os metadados do arquivo original.
        #
        # Isso é proposital para conseguirmos restaurar
        # posteriormente o estado ReadOnly.
        #

        shutil.copy2(
            setup_project_path,
            backup_path,
        )

        return backup_path

    def replace_original(
        self,
        prepared_setup_project_path: Path,
        original_setup_project_path: Path,
    ) -> None:
        """
        Substitui temporariamente o projeto original pelo
        projeto preparado.

        O arquivo original pode estar marcado como ReadOnly.
        Portanto, o atributo é removido antes da substituição.

        O original deve ter sido previamente salvo através
        de backup_original().
        """

        if prepared_setup_project_path is None:
            raise ValueError(
                "Projeto Setup preparado não foi informado."
            )

        if original_setup_project_path is None:
            raise ValueError(
                "Projeto Setup original não foi informado."
            )

        prepared_setup_project_path = Path(
            prepared_setup_project_path,
        )

        original_setup_project_path = Path(
            original_setup_project_path,
        )

        if not prepared_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup preparado não encontrado: "
                f"{prepared_setup_project_path}"
            )

        if not prepared_setup_project_path.is_file():
            raise ValueError(
                "Projeto Setup preparado não é um arquivo: "
                f"{prepared_setup_project_path}"
            )

        if not original_setup_project_path.exists():
            raise FileNotFoundError(
                "Projeto Setup original não encontrado: "
                f"{original_setup_project_path}"
            )

        #
        # O arquivo original pode estar ReadOnly
        # devido ao TFS/TFVC.
        #

        self.__make_writable(
            original_setup_project_path,
        )

        #
        # Não usamos copy2() aqui porque não queremos
        # transferir os atributos do arquivo preparado
        # para o arquivo original.
        #

        shutil.copyfile(
            prepared_setup_project_path,
            original_setup_project_path,
        )

        #
        # Garante que o arquivo temporariamente utilizado
        # pelo Visual Studio seja gravável.
        #

        self.__make_writable(
            original_setup_project_path,
        )

    def restore_original(
        self,
        backup_path: Path,
        original_setup_project_path: Path,
    ) -> None:
        """
        Restaura o projeto Setup original a partir
        do backup.

        O método também restaura o atributo ReadOnly
        existente no arquivo original.

        Este método deve ser chamado dentro de um
        bloco finally.
        """

        if backup_path is None:
            raise ValueError(
                "Backup do projeto Setup não foi informado."
            )

        if original_setup_project_path is None:
            raise ValueError(
                "Projeto Setup original não foi informado."
            )

        backup_path = Path(
            backup_path,
        )

        original_setup_project_path = Path(
            original_setup_project_path,
        )

        if not backup_path.exists():
            raise FileNotFoundError(
                "Backup do projeto Setup não encontrado: "
                f"{backup_path}"
            )

        if not backup_path.is_file():
            raise ValueError(
                "Backup do projeto Setup não é um arquivo: "
                f"{backup_path}"
            )

        #
        # Captura os atributos do backup.
        #
        # Como backup_original() utilizou copy2(),
        # o modo contém o estado original do arquivo.
        #

        backup_mode = (
            backup_path.stat().st_mode
        )

        #
        # O arquivo original pode estar sendo usado como
        # arquivo preparado e, portanto, pode estar ReadOnly
        # ou ter outro estado de permissão.
        #

        if original_setup_project_path.exists():

            self.__make_writable(
                original_setup_project_path,
            )

        #
        # Restaura somente o conteúdo.
        #

        shutil.copyfile(
            backup_path,
            original_setup_project_path,
        )

        #
        # Restaura o modo/permissão original.
        #
        # No Windows isso restaura principalmente o estado
        # ReadOnly representado pelo bit de escrita.
        #

        os.chmod(
            original_setup_project_path,
            stat.S_IMODE(
                backup_mode,
            ),
        )

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

        #
        # O arquivo pode ter sido criado a partir de uma
        # origem ReadOnly. Garante que ele seja gravável
        # antes da escrita.
        #

        if workspace_project_path.exists():
            self.__make_writable(
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

        #
        # Arquivos do workspace podem ter sido criados
        # com atributos ReadOnly.
        #
        # Antes da remoção, torna os arquivos graváveis.
        #

        self.__make_tree_writable(
            workspace_root,
        )

        shutil.rmtree(
            workspace_root,
        )

    @staticmethod
    def __make_writable(
        file_path: Path,
    ) -> None:
        """
        Remove o atributo ReadOnly de um arquivo.
        """

        file_path = Path(
            file_path,
        )

        if not file_path.exists():
            return

        current_mode = (
            file_path.stat().st_mode
        )

        os.chmod(
            file_path,
            current_mode
            | stat.S_IWRITE,
        )

    @classmethod
    def __make_tree_writable(
        cls,
        root_path: Path,
    ) -> None:
        """
        Remove o atributo ReadOnly de todos os arquivos
        e diretórios dentro do workspace.
        """

        root_path = Path(
            root_path,
        )

        if not root_path.exists():
            return

        #
        # Primeiro arquivos.
        #

        for path in root_path.rglob("*"):

            try:

                cls.__make_writable(
                    path,
                )

            except OSError:
                #
                # A remoção será tentada posteriormente
                # pelo shutil.rmtree().
                #

                pass

        #
        # Finalmente o próprio diretório.
        #

        try:

            current_mode = (
                root_path.stat().st_mode
            )

            os.chmod(
                root_path,
                current_mode
                | stat.S_IWRITE,
            )

        except OSError:
            pass