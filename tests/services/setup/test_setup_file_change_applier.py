"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file_change_applier.py
Descrição : Testes do SetupFileChangeApplier.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.setup_file_change_applier import (
    SetupFileChangeApplier,
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

from app.services.setup.vdproj_file_template_provider import (
    VdprojFileTemplateProvider,
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

    "{BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB}:_22222222222222222222222222222222"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Outra, Version=1.0.0.0"

        "ScatterAssemblies"
        {
            "_222222"
            {
                "Name" = "8:Outra.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Outra.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_BBBBBB"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
"""


def create_applier():
    """
    Cria o ChangeApplier com as dependências reais.
    """

    parser = (
        VdprojBlockParser()
    )

    return SetupFileChangeApplier(
        modifier=(
            VdprojFileModifier(
                parser=parser,
            )
        ),
        template_provider=(
            VdprojFileTemplateProvider(
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


def create_update():
    """
    Cria uma alteração UPDATE.
    """

    return SetupFileSync(
        name="Existente.dll",
        source_path="Existente.dll",
        publish_path=Path(
            r"C:\Publish\Existente.dll"
        ),
        assembly_display_name=(
            "Existente, Version=10.4.8.0"
        ),
        action=SetupFileAction.UPDATE,
    )


def create_remove():
    """
    Cria uma alteração REMOVE.
    """

    return SetupFileSync(
        name="Outra.dll",
        source_path="Outra.dll",
        publish_path=Path(
            r"C:\Publish\Outra.dll"
        ),
        action=SetupFileAction.REMOVE,
    )


def create_add():
    """
    Cria uma alteração ADD.
    """

    return SetupFileSync(
        name="Nova.dll",
        source_path="Nova.dll",
        publish_path=Path(
            r"C:\Publish\Nova.dll"
        ),
        assembly_display_name=(
            "Nova, Version=10.4.8.0"
        ),
        action=SetupFileAction.ADD,
    )


def test_deve_aplicar_update():
    """
    Deve aplicar UPDATE no bloco existente.
    """

    applier = create_applier()

    result = applier.apply(
        content=CONTENT,
        changes=[
            create_update(),
        ],
        template_file_name="Existente.dll",
    )

    assert (
        '"SourcePath" = "8:Existente.dll"'
        in result
    )

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:Existente, Version=10.4.8.0"'
        in result
    )


def test_deve_aplicar_remove():
    """
    Deve remover o bloco existente.
    """

    applier = create_applier()

    result = applier.apply(
        content=CONTENT,
        changes=[
            create_remove(),
        ],
        template_file_name="Existente.dll",
    )

    assert (
        '"Outra.dll"'
        not in result
    )

    assert (
    '"Name" = "8:Existente.dll"'
    in result
    )

    assert (
        '"DefaultLocation"'
        in result
    )


def test_deve_aplicar_add():
    """
    Deve adicionar um novo arquivo utilizando
    o arquivo existente como template.
    """

    applier = create_applier()

    result = applier.apply(
        content=CONTENT,
        changes=[
            create_add(),
        ],
        template_file_name="Existente.dll",
    )

    assert (
        '"Name" = "8:Nova.dll"'
        in result
    )

    assert (
        '"SourcePath" = "8:Nova.dll"'
        in result
    )

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:Nova, Version=10.4.8.0"'
        in result
    )

    assert (
        '"Name" = "8:Existente.dll"'
        in result
    )

    assert (
        '"Name" = "8:Outra.dll"'
        in result
    )


def test_deve_aplicar_multiplas_alteracoes():
    """
    Deve aplicar UPDATE, REMOVE e ADD
    em arquivos diferentes.
    """

    applier = create_applier()

    result = applier.apply(
        content=CONTENT,
        changes=[
            create_update(),
            create_remove(),
            create_add(),
        ],
        template_file_name="Existente.dll",
    )

    #
    # UPDATE
    #

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:Existente, Version=10.4.8.0"'
        in result
    )

    #
    # REMOVE
    #

    assert (
        '"Name" = "8:Outra.dll"'
        not in result
    )

    #
    # ADD
    #

    assert (
        '"Name" = "8:Nova.dll"'
        in result
    )

    assert (
        '"SourcePath" = "8:Nova.dll"'
        in result
    )

    #
    # Arquivo original utilizado
    # como template continua existindo.
    #

    assert (
        '"Name" = "8:Existente.dll"'
        in result
    )


def test_deve_preservar_conteudo_do_filesystem():
    """
    Deve preservar a estrutura principal do FileSystem.
    """

    applier = create_applier()

    result = applier.apply(
        content=CONTENT,
        changes=[
            create_update(),
            create_remove(),
            create_add(),
        ],
        template_file_name="Existente.dll",
    )

    assert (
        '"FileSystem"'
        in result
    )

    assert (
        '"DefaultLocation" = '
        '"8:[ProgramFilesFolder][Manufacturer]\\[ProductName]"'
        in result
    )


def test_deve_rejeitar_conteudo_none():
    """
    Deve rejeitar conteúdo não informado.
    """

    applier = create_applier()

    with pytest.raises(
        ValueError,
        match="Conteúdo do .vdproj não foi informado.",
    ):
        applier.apply(
            content=None,
            changes=[],
            template_file_name="Existente.dll",
        )


def test_deve_rejeitar_alteracoes_none():
    """
    Deve rejeitar alterações não informadas.
    """

    applier = create_applier()

    with pytest.raises(
        ValueError,
        match="Alterações não foram informadas.",
    ):
        applier.apply(
            content=CONTENT,
            changes=None,
            template_file_name="Existente.dll",
        )


def test_deve_rejeitar_template_nao_informado():
    """
    Deve rejeitar arquivo template não informado.
    """

    applier = create_applier()

    with pytest.raises(
        ValueError,
        match="Arquivo template não foi informado.",
    ):
        applier.apply(
            content=CONTENT,
            changes=[],
            template_file_name="",
        )