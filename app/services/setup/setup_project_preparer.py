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
        # ============================================================
        # 1. Criar cópia do .vdproj.
        # ============================================================
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
        # ============================================================
        # 2. Carregar os arquivos existentes
        #    no .vdproj.
        # ============================================================
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
        # ============================================================
        # 3. Calcular as alterações comparando
        #    com o publish_path.
        # ============================================================
        #

        changes = (
            self.__synchronizer.synchronize(
                setup_files=setup_files,
                publish_path=publish_path,
            )
        )

        #
        # ============================================================
        # DIAGNÓSTICO DAS ALTERAÇÕES
        # ============================================================
        #

        print()
        print(
            "=" * 70
        )

        print(
            "[OuroBuild] SETUP PROJECT PREPARER"
        )

        print(
            "=" * 70
        )

        print(
            "[OuroBuild] Projeto original:"
        )

        print(
            f"[OuroBuild] {setup_project_path}"
        )

        print(
            "[OuroBuild] Workspace:"
        )

        print(
            f"[OuroBuild] {workspace_project}"
        )

        print(
            "[OuroBuild] Publish Path:"
        )

        print(
            f"[OuroBuild] {publish_path}"
        )

        print(
            "[OuroBuild] Arquivos encontrados no Setup:"
        )

        print(
            f"[OuroBuild] {len(setup_files)}"
        )

        print(
            "[OuroBuild] Alterações calculadas:"
        )

        print(
            f"[OuroBuild] {len(changes)}"
        )

        #
        # Mostra cada alteração.
        #

        for index, change in enumerate(
            changes
        ):

            print(
                f"[OuroBuild] "
                f"CHANGE [{index}]"
            )

            print(
                f"[OuroBuild]   name: "
                f"{change.name}"
            )

            print(
                f"[OuroBuild]   action: "
                f"{change.action}"
            )

            print(
                f"[OuroBuild]   source_path: "
                f"{change.source_path}"
            )

            print(
                f"[OuroBuild]   publish_path: "
                f"{change.publish_path}"
            )

            print(
                f"[OuroBuild]   assembly_display_name: "
                f"{change.assembly_display_name}"
            )

        print(
            "=" * 70
        )

        #
        # ============================================================
        # 4. Ler a cópia de trabalho.
        # ============================================================
        #

        content = (
            self.__workspace_service.read(
                workspace_project_path=(
                    workspace_project
                ),
            )
        )

        #
        # Guardamos o conteúdo original da cópia
        # antes de qualquer alteração.
        #

        original_workspace_content = (
            content
        )

        #
        # ============================================================
        # DIAGNÓSTICO DO VDPROJ ORIGINAL
        # ============================================================
        #

        self.__print_vdproj_diagnostics(
            title=(
                "[OuroBuild] VDPROJ "
                "ANTES DAS ALTERAÇÕES"
            ),
            content=(
                original_workspace_content
            ),
        )

        #
        # ============================================================
        # 5. Aplicar UPDATE / REMOVE / ADD.
        # ============================================================
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
        # ============================================================
        # DIAGNÓSTICO DO VDPROJ PREPARADO
        # ============================================================
        #

        self.__print_vdproj_diagnostics(
            title=(
                "[OuroBuild] VDPROJ "
                "DEPOIS DAS ALTERAÇÕES"
            ),
            content=(
                prepared_content
            ),
        )

        #
        # ============================================================
        # COMPARAÇÃO
        # ============================================================
        #

        print()
        print(
            "=" * 70
        )

        print(
            "[OuroBuild] COMPARAÇÃO DO VDPROJ"
        )

        print(
            "=" * 70
        )

        print(
            "[OuroBuild] Tamanho antes:"
        )

        print(
            f"[OuroBuild] "
            f"{len(original_workspace_content)} "
            f"caracteres"
        )

        print(
            "[OuroBuild] Tamanho depois:"
        )

        print(
            f"[OuroBuild] "
            f"{len(prepared_content)} "
            f"caracteres"
        )

        print(
            "[OuroBuild] Conteúdo alterado:"
        )

        print(
            f"[OuroBuild] "
            f"{original_workspace_content != prepared_content}"
        )

        #
        # Verifica especificamente as propriedades Scc.
        #

        original_scc = (
            self.__get_scc_lines(
                original_workspace_content,
            )
        )

        prepared_scc = (
            self.__get_scc_lines(
                prepared_content,
            )
        )

        print()
        print(
            "[OuroBuild] Scc ANTES:"
        )

        if original_scc:

            for line in original_scc:

                print(
                    f"[OuroBuild] {line}"
                )

        else:

            print(
                "[OuroBuild] "
                "<nenhuma propriedade Scc encontrada>"
            )

        print()
        print(
            "[OuroBuild] Scc DEPOIS:"
        )

        if prepared_scc:

            for line in prepared_scc:

                print(
                    f"[OuroBuild] {line}"
                )

        else:

            print(
                "[OuroBuild] "
                "<nenhuma propriedade Scc encontrada>"
            )

        print(
            "=" * 70
        )

        #
        # ============================================================
        # 6. Salvar somente a cópia.
        # ============================================================
        #

        self.__workspace_service.write(
            workspace_project_path=(
                workspace_project
            ),
            content=prepared_content,
        )

        #
        # ============================================================
        # CONFIRMAÇÃO DO ARQUIVO PREPARADO
        # ============================================================
        #

        print()
        print(
            "=" * 70
        )

        print(
            "[OuroBuild] VDPROJ PREPARADO SALVO"
        )

        print(
            "=" * 70
        )

        print(
            "[OuroBuild] Caminho:"
        )

        print(
            f"[OuroBuild] {workspace_project}"
        )

        try:

            saved_content = (
                workspace_project.read_text(
                    encoding="utf-8",
                )
            )

            print(
                "[OuroBuild] Tamanho salvo:"
            )

            print(
                f"[OuroBuild] "
                f"{len(saved_content)} caracteres"
            )

            print(
                "[OuroBuild] SccProvider:"
            )

            scc_lines = (
                self.__get_scc_lines(
                    saved_content,
                )
            )

            if scc_lines:

                for line in scc_lines:

                    print(
                        f"[OuroBuild] {line}"
                    )

            else:

                print(
                    "[OuroBuild] "
                    "<nenhum Scc encontrado>"
                )

        except Exception as error:

            print(
                "[OuroBuild] Não foi possível "
                "ler o arquivo preparado após salvar:"
            )

            print(
                f"[OuroBuild] {error}"
            )

        print(
            "=" * 70
        )

        return workspace_project

    @staticmethod
    def __get_scc_lines(
        content: str,
    ) -> list[str]:
        """
        Retorna todas as linhas relacionadas a Scc.

        Usado somente para diagnóstico.
        """

        if not content:
            return []

        return [
            line
            for line in content.splitlines()
            if "Scc" in line
        ]

    @staticmethod
    def __print_vdproj_diagnostics(
        title: str,
        content: str,
    ) -> None:
        """
        Exibe informações básicas de diagnóstico
        do conteúdo do .vdproj.
        """

        print()
        print(
            "=" * 70
        )

        print(
            title
        )

        print(
            "=" * 70
        )

        print(
            "[OuroBuild] Tamanho:"
        )

        print(
            f"[OuroBuild] "
            f"{len(content)} caracteres"
        )

        print(
            "[OuroBuild] Propriedades Scc:"
        )

        scc_lines = (
            SetupProjectPreparer
            .__get_scc_lines(
                content,
            )
        )

        if scc_lines:

            for line in scc_lines:

                print(
                    f"[OuroBuild] {line}"
                )

        else:

            print(
                "[OuroBuild] "
                "<nenhuma propriedade Scc encontrada>"
            )

        print(
            "=" * 70
        )