"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_file_modifier.py
Descrição : Testes do VdprojFileModifier.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_file_modifier import (
    VdprojFileModifier,
)


CONTENT = """
"File"
{
    "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Custom.Framework, Version=4.0.0.0"

        "ScatterAssemblies"
        {
            "_111111"
            {
                "Name" = "8:Custom.Framework.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Custom.Framework.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_AAAAAA"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
"""


def create_modifier():
    """
    Cria o Modifier com o parser real.
    """

    parser = (
        VdprojBlockParser()
    )

    return VdprojFileModifier(
        parser=parser,
    )


def create_setup_file():
    """
    Cria um SetupFileSync para teste.
    """

    return SetupFileSync(
        name="Custom.Framework.dll",
        source_path="Custom.Framework.dll",
        publish_path=Path(
            r"C:\Publish\Custom.Framework.dll"
        ),
        assembly_display_name=(
            "Custom.Framework, Version=10.4.8.0, "
            "Culture=neutral, "
            "PublicKeyToken=81568928c6d92f5f, "
            "processorArchitecture=MSIL"
        ),
        action=SetupFileAction.UPDATE,
    )


def test_deve_atualizar_source_path():
    """
    Deve atualizar o SourcePath utilizando
    o source_path do SetupFile.
    """

    modifier = create_modifier()

    setup_file = create_setup_file()

    result = modifier.update(
        content=CONTENT,
        setup_file=setup_file,
    )

    assert (
        '"SourcePath" = "8:Custom.Framework.dll"'
        in result
    )

    assert (
        r"C:\Publish\Custom.Framework.dll"
        not in result
    )


def test_deve_atualizar_assembly_display_name():
    """
    Deve atualizar o AssemblyAsmDisplayName.
    """

    modifier = create_modifier()

    setup_file = create_setup_file()

    result = modifier.update(
        content=CONTENT,
        setup_file=setup_file,
    )

    assert (
        '"AssemblyAsmDisplayName" = '
        '"8:Custom.Framework, Version=10.4.8.0, '
        'Culture=neutral, '
        'PublicKeyToken=81568928c6d92f5f, '
        'processorArchitecture=MSIL"'
        in result
    )


def test_nao_deve_alterar_conteudo_fora_do_bloco():
    """
    Deve preservar o restante do .vdproj.
    """

    modifier = create_modifier()

    setup_file = create_setup_file()

    result = modifier.update(
        content=CONTENT,
        setup_file=setup_file,
    )

    assert '"File"' in result

    assert (
        '"Folder" = "8:_AAAAAA"'
        in result
    )

    assert (
        '"Vital" = "11:TRUE"'
        in result
    )


def test_deve_rejeitar_conteudo_none():
    """
    Deve rejeitar conteúdo não informado.
    """

    modifier = create_modifier()

    setup_file = create_setup_file()

    try:
        modifier.update(
            content=None,
            setup_file=setup_file,
        )

        assert False

    except ValueError as exception:

        assert (
            str(exception)
            == "Conteúdo do .vdproj não foi informado."
        )


def test_deve_rejeitar_setup_file_none():
    """
    Deve rejeitar SetupFileSync não informado.
    """

    modifier = create_modifier()

    try:
        modifier.update(
            content=CONTENT,
            setup_file=None,
        )

        assert False

    except ValueError as exception:

        assert (
            str(exception)
            == "SetupFileSync não foi informado."
        )
def test_deve_remover_bloco_do_arquivo():
    """
    Deve remover somente o bloco do arquivo informado.
    """

    modifier = create_modifier()

    setup_file = create_setup_file()

    result = modifier.remove(
        content=CONTENT,
        setup_file=setup_file,
    )

    assert (
        '"Custom.Framework.dll"'
        not in result
    )

    assert (
        '"AssemblyAsmDisplayName"'
        not in result
    )

    assert (
        '"Folder" = "8:_AAAAAA"'
        not in result
    )

    assert (
        '"File"'
        in result
    )