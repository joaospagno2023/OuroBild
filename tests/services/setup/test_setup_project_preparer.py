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