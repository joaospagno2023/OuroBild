"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_project_preparer.py
Descrição : Prepara uma cópia de trabalho do projeto .vdproj
            utilizando os arquivos existentes no publish_path.
--------------------------------------------------------------------
"""


from pathlib import Path


from app.models.setup.setup_file import (
    SetupFile,
)

from app.services.setup.setup_file_change_applier import (
    SetupFileChangeApplier,
)

from app.services.setup.setup_file_synchronizer import (
    SetupFileSynchronizer,
)

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.vdproj_setup_file_loader import (
    VdprojSetupFileLoader,
)


class SetupProjectPreparer:
    """
    Prepara uma cópia de trabalho do projeto .vdproj.

    O projeto original nunca é alterado.

    O fluxo é:

        .vdproj original
            ↓
        cópia temporária
            ↓
        leitura dos arquivos
            ↓
        comparação com publish_path
            ↓
        UPDATE / REMOVE / ADD
            ↓
        .vdproj preparado
    """

    def __init__(
        self,
        workspace_service: SetupWorkspaceService,
        setup_file_loader: VdprojSetupFileLoader,
        synchronizer: SetupFileSynchronizer,
        change_applier: SetupFileChangeApplier,
    ) -> None:
        """
        Inicializa o preparador.
        """

        if workspace_service is None:
            raise ValueError(
                "SetupWorkspaceService "
                "não foi informado."
            )

        if setup_file_loader is None:
            raise ValueError(
                "VdprojSetupFileLoader "
                "não foi informado."
            )

        if synchronizer is None:
            raise ValueError(
                "SetupFileSynchronizer "
                "não foi informado."
            )

        if change_applier is None:
            raise ValueError(
                "SetupFileChangeApplier "
                "não foi informado."
            )

        self.__workspace_service = (
            workspace_service
        )

        self.__setup_file_loader = (
            setup_file_loader
        )

        self.__synchronizer = (
            synchronizer
        )

        self.__change_applier = (
            change_applier
        )

    def prepare(
        self,
        setup_project_path: Path,
        publish_path: Path,
        workspace_root: Path,
        template_file_name: str,
    ) -> Path:
        """
        Prepara uma cópia do projeto .vdproj.

        O arquivo original permanece intacto.

        Returns:
            Caminho do .vdproj preparado.
        """

        if setup_project_path is None:
            raise ValueError(
                "SetupProjectPath "
                "não foi informado."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath "
                "não foi informado."
            )

        if workspace_root is None:
            raise ValueError(
                "WorkspaceRoot "
                "não foi informado."
            )

        if not template_file_name:
            raise ValueError(
                "Arquivo template "
                "não foi informado."
            )

        #
        # 1. Criar cópia do .vdproj.
        #

        workspace_project = (
            self.__workspace_service
            .create_workspace(
                setup_project_path=(
                    setup_project_path
                ),
                workspace_root=(
                    workspace_root
                ),
            )
        )

        #
        # 2. Carregar os arquivos existentes
        #    no .vdproj.
        #

        setup_files = (
            self.__setup_file_loader.load(
                setup_project_path=(
                    workspace_project
                ),
                publish_path=publish_path,
            )
        )

        #
        # 3. Calcular as alterações comparando
        #    com o publish_path.
        #

        changes = (
            self.__synchronizer.synchronize(
                setup_files=setup_files,
                publish_path=publish_path,
            )
        )

        #
        # 4. Ler a cópia de trabalho.
        #

        content = (
            self.__workspace_service.read(
                workspace_project_path=(
                    workspace_project
                ),
            )
        )

        #
        # 5. Aplicar UPDATE / REMOVE / ADD.
        #

        prepared_content = (
            self.__change_applier.apply(
                content=content,
                changes=changes,
                template_file_name=(
                    template_file_name
                ),
            )
        )

        #
        # 6. Salvar somente a cópia.
        #

        self.__workspace_service.write(
            workspace_project_path=(
                workspace_project
            ),
            content=prepared_content,
        )

        return workspace_project