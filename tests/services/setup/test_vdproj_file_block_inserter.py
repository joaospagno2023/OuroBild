"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_file_block_inserter.py
Descrição : Testes do VdprojFileBlockInserter.
--------------------------------------------------------------------
"""

import pytest

from app.services.setup.vdproj_file_block_inserter import (
    VdprojFileBlockInserter,
)


CONTENT = """
"FileSystem"
{
    "DefaultLocation" = "8:[ProgramFilesFolder][Manufacturer]\\[ProductName]"

    "Components"
    {
        "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
        {
            "SourcePath" = "8:Existente.dll"
        }
    }
}
"""


NEW_BLOCK = """
    "{BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB}:_22222222222222222222222222222222"
    {
        "SourcePath" = "8:Nova.dll"
    }
"""


def test_deve_inserir_bloco():
    """
    Deve inserir o novo bloco no conteúdo.
    """

    inserter = (
        VdprojFileBlockInserter()
    )

    result = inserter.insert(
        content=CONTENT,
        file_block=NEW_BLOCK,
    )

    assert (
        '"SourcePath" = "8:Nova.dll"'
        in result
    )

    assert (
        '"SourcePath" = "8:Existente.dll"'
        in result
    )


def test_deve_preservar_conteudo_original():
    """
    Deve preservar o conteúdo existente.
    """

    inserter = (
        VdprojFileBlockInserter()
    )

    result = inserter.insert(
        content=CONTENT,
        file_block=NEW_BLOCK,
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

    inserter = (
        VdprojFileBlockInserter()
    )

    with pytest.raises(
        ValueError,
        match="Conteúdo do .vdproj não foi informado.",
    ):
        inserter.insert(
            content=None,
            file_block=NEW_BLOCK,
        )


def test_deve_rejeitar_bloco_vazio():
    """
    Deve rejeitar bloco não informado.
    """

    inserter = (
        VdprojFileBlockInserter()
    )

    with pytest.raises(
        ValueError,
        match="Bloco do arquivo não foi informado.",
    ):
        inserter.insert(
            content=CONTENT,
            file_block="",
        )