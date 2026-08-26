"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_project_preparer.py
Descrição : Testes do SetupProjectPreparer.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.setup_file_change_applier import (
    SetupFileChangeApplier,
)

from app.services.setup.setup_file_synchronizer import (
    SetupFileSynchronizer,
)

from app.services.setup.setup_file_template_provider import (
    SetupFileTemplateProvider,
)

from app.services.setup.setup_project_preparer import (
    SetupProjectPreparer,
)

from app.services.setup.setup_workspace_service import (
    SetupWorkspaceService,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_component_identity_generator import (
    VdprojComponentIdentityGenerator,
)

from app.services.setup.vdproj_file_block_builder import (
    VdprojFileBlockBuilder,
)

from app.services.setup.vdproj_file_block_inserter import (
    VdprojFileBlockInserter,
)

from app.services.setup.vdproj_file_modifier import (
    VdprojFileModifier,
)

from app.services.setup.vdproj_setup_file_loader import (
    VdprojSetupFileLoader,
)


CONTENT = """
"FileSystem"
{
    "DefaultLocation" = "8:[ProgramFilesFolder][Manufacturer]\\[ProductName]"

    "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Existente, Version=1.0.0.0"

        "ScatterAssemblies"
        {
            "_111111"
            {
                "Name" = "8:Existente.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Existente.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_AAAAAA"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
"""


def create_preparer():
    """
    Cria o SetupProjectPreparer
    utilizando as implementações reais.
    """

    parser = (
        VdprojBlockParser()
    )

    change_applier = (
        SetupFileChangeApplier(
            modifier=(
                VdprojFileModifier(
                    parser=parser,
                )
            ),
            template_provider=(
                SetupFileTemplateProvider(
                    parser=parser,
                )
            ),
            identity_generator=(
                VdprojComponentIdentityGenerator()
            ),
            block_builder=(
                VdprojFileBlockBuilder()
            ),
            block_inserter=(
                VdprojFileBlockInserter()
            ),
        )
    )

    setup_file_loader = (
        VdprojSetupFileLoader(
            parser=parser,
        )
    )

    return SetupProjectPreparer(
        workspace_service=(
            SetupWorkspaceService()
        ),
        setup_file_loader=(
            setup_file_loader
        ),
        synchronizer=(
            SetupFileSynchronizer()
        ),
        change_applier=(
            change_applier
        ),
    )


def test_deve_preparar_copia_do_setup(
    tmp_path: Path,
):
    """
    Deve criar uma cópia do Setup e aplicar
    as alterações nela.
    """

    setup_project = (
        tmp_path
        / "Setup.vdproj"
    )

    setup_project.write_text(
        CONTENT,
        encoding="utf-8",
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    (
        publish_path
        / "Existente.dll"
    ).write_text(
        "nova dll",
        encoding="utf-8",
    )

    workspace_root = (
        tmp_path
        / "workspace"
    )

    preparer = create_preparer()

    result = preparer.prepare(
        setup_project_path=setup_project,
        publish_path=publish_path,
        workspace_root=workspace_root,
        template_file_name="Existente.dll",
    )

    assert result.exists()

    assert result != setup_project

    prepared_content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        '"Name" = "8:Existente.dll"'
        in prepared_content
    )

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:Existente, Version=1.0.0.0"'
        in prepared_content
    )

    original_content = (
        setup_project.read_text(
            encoding="utf-8",
        )
    )

    assert (
        original_content
        == CONTENT
    )


def test_deve_utilizar_publish_path(
    tmp_path: Path,
):
    """
    Deve utilizar o publish_path como fonte
    dos arquivos.
    """

    setup_project = (
        tmp_path
        / "Setup.vdproj"
    )

    setup_project.write_text(
        CONTENT,
        encoding="utf-8",
    )

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    (
        publish_path
        / "Existente.dll"
    ).write_text(
        "DLL",
        encoding="utf-8",
    )

    workspace_root = (
        tmp_path
        / "workspace"
    )

    preparer = create_preparer()

    result = preparer.prepare(
        setup_project_path=setup_project,
        publish_path=publish_path,
        workspace_root=workspace_root,
        template_file_name="Existente.dll",
    )

    assert result.exists()


def test_deve_rejeitar_setup_project_none(
    tmp_path: Path,
):
    """
    Deve rejeitar SetupProjectPath não informado.
    """

    preparer = create_preparer()

    publish_path = (
        tmp_path
        / "publish"
    )

    publish_path.mkdir()

    with pytest.raises(
        ValueError,
        match="SetupProjectPath não foi informado.",
    ):
        preparer.prepare(
            setup_project_path=None,
            publish_path=publish_path,
            workspace_root=(
                tmp_path
                / "workspace"
            ),
            template_file_name="Existente.dll",
        )
def test_deve_remover_vinculo_scc_da_copia_temporaria(
    tmp_path: Path,
) -> None:
    """
    O VDPROJ temporário não deve manter o vínculo
    com o Source Control/TFS.

    O arquivo original deve permanecer inalterado.
    """

    setup_project = (
        tmp_path
        / "Original"
        / "Setup.vdproj"
    )

    publish_path = (
        tmp_path
        / "bin"
        / "Release"
    )

    workspace_root = (
        tmp_path
        / ".ourobuild"
    )

    setup_project.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    publish_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    content_original = """\
"DeployProject" = "8:Start"
"ProductCode" = "8:{TEST}"
"SccProjectName" = "8:SAK"
"SccLocalPath" = "8:SAK"
"SccAuxPath" = "8:SAK"
"SccProvider" = "8:SAK"
"Root" = "8:End"
"""

    setup_project.write_text(
        content_original,
        encoding="utf-8",
    )

    #
    # Aqui usamos mocks simples das dependências
    # do SetupProjectPreparer.
    #

    class FakeWorkspaceService:

        def create_workspace(
            self,
            setup_project_path: Path,
            workspace_root: Path,
        ) -> Path:

            workspace = (
                workspace_root
                / setup_project.name
            )

            workspace.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            workspace.write_text(
                setup_project.read_text(
                    encoding="utf-8",
                ),
                encoding="utf-8",
            )

            return workspace

        def read(
            self,
            workspace_project_path: Path,
        ) -> str:

            return workspace_project_path.read_text(
                encoding="utf-8",
            )

        def write(
            self,
            workspace_project_path: Path,
            content: str,
        ) -> None:

            workspace_project_path.write_text(
                content,
                encoding="utf-8",
            )

    class FakeLoader:

        def load(
            self,
            setup_project_path: Path,
            publish_path: Path,
        ) -> list:

            return []

    class FakeSynchronizer:

        def synchronize(
            self,
            setup_files: list,
            publish_path: Path,
        ) -> list:

            return []

    class FakeChangeApplier:

        def apply(
            self,
            content: str,
            changes: list,
            template_file_name: str,
        ) -> str:

            return content

    service = SetupProjectPreparer(
        workspace_service=(
            FakeWorkspaceService()
        ),
        setup_file_loader=(
            FakeLoader()
        ),
        synchronizer=(
            FakeSynchronizer()
        ),
        change_applier=(
            FakeChangeApplier()
        ),
    )

    result = service.prepare(
        setup_project_path=setup_project,
        publish_path=publish_path,
        workspace_root=workspace_root,
        template_file_name="Template.dll",
    )

    #
    # O arquivo original NÃO pode ter sido alterado.
    #

    original_after = (
        setup_project.read_text(
            encoding="utf-8",
        )
    )

    assert (
        original_after
        == content_original
    )

    #
    # A cópia temporária deve existir.
    #

    assert result.exists()

    #
    # A cópia não pode possuir os vínculos Scc.
    #

    prepared_content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        '"SccProjectName"'
        not in prepared_content
    )

    assert (
        '"SccLocalPath"'
        not in prepared_content
    )

    assert (
        '"SccAuxPath"'
        not in prepared_content
    )

    assert (
        '"SccProvider"'
        not in prepared_content
    )

    #
    # O restante do VDPROJ deve permanecer.
    #

    assert (
        '"DeployProject" = "8:Start"'
        in prepared_content
    )

    assert (
        '"ProductCode" = "8:{TEST}"'
        in prepared_content
    )

    assert (
        '"Root" = "8:End"'
        in prepared_content
    )
def test_deve_remover_vinculo_scc_do_csproj_temporario(
    tmp_path: Path,
) -> None:
    """
    O .csproj temporário não deve manter o vínculo
    com o Source Control/TFS.

    O arquivo original deve permanecer inalterado.
    """

    project = (
        tmp_path
        / "Original"
        / "OuroNet.Client.WinService.LinkPagamento.csproj"
    )

    publish_path = (
        tmp_path
        / "bin"
        / "Release"
    )

    workspace_root = (
        tmp_path
        / ".ourobuild"
    )

    project.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    publish_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    content_original = """\
<Project ToolsVersion="15.0">
  <PropertyGroup>
    <SccProjectName>SAK</SccProjectName>
    <SccLocalPath>SAK</SccLocalPath>
    <SccAuxPath>SAK</SccAuxPath>
    <SccProvider>SAK</SccProvider>
    <Configuration>Release</Configuration>
  </PropertyGroup>
</Project>
"""

    project.write_text(
        content_original,
        encoding="utf-8",
    )

    #
    # O arquivo temporário simula a cópia criada
    # pelo WorkspaceService.
    #

    class FakeWorkspaceService:

        def create_workspace(
            self,
            setup_project_path: Path,
            workspace_root: Path,
        ) -> Path:

            workspace = (
                workspace_root
                / setup_project_path.name
            )

            workspace.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            workspace.write_text(
                setup_project_path.read_text(
                    encoding="utf-8",
                ),
                encoding="utf-8",
            )

            return workspace

        def read(
            self,
            workspace_project_path: Path,
        ) -> str:

            return workspace_project_path.read_text(
                encoding="utf-8",
            )

        def write(
            self,
            workspace_project_path: Path,
            content: str,
        ) -> None:

            workspace_project_path.write_text(
                content,
                encoding="utf-8",
            )

    class FakeLoader:

        def load(
            self,
            setup_project_path: Path,
            publish_path: Path,
        ) -> list:
            return []

    class FakeSynchronizer:

        def synchronize(
            self,
            setup_files: list,
            publish_path: Path,
        ) -> list:
            return []

    class FakeChangeApplier:

        def apply(
            self,
            content: str,
            changes: list,
            template_file_name: str,
        ) -> str:
            return content

    service = SetupProjectPreparer(
        workspace_service=(
            FakeWorkspaceService()
        ),
        setup_file_loader=(
            FakeLoader()
        ),
        synchronizer=(
            FakeSynchronizer()
        ),
        change_applier=(
            FakeChangeApplier()
        ),
    )

    result = service.prepare(
        setup_project_path=project,
        publish_path=publish_path,
        workspace_root=workspace_root,
        template_file_name="Template.dll",
    )

    #
    # O original não pode ser alterado.
    #

    original_after = (
        project.read_text(
            encoding="utf-8",
        )
    )

    assert (
        original_after
        == content_original
    )

    #
    # A cópia temporária deve existir.
    #

    assert result.exists()

    #
    # A cópia temporária não pode possuir
    # nenhuma propriedade Scc.
    #

    prepared_content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "<SccProjectName>"
        not in prepared_content
    )

    assert (
        "<SccLocalPath>"
        not in prepared_content
    )

    assert (
        "<SccAuxPath>"
        not in prepared_content
    )

    assert (
        "<SccProvider>"
        not in prepared_content
    )

    #
    # O restante do arquivo deve permanecer.
    #

    assert (
        "<Configuration>Release</Configuration>"
        in prepared_content
    )