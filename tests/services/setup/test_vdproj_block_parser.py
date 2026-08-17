"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_block_parser.py
Descrição : Testes do VdprojBlockParser.
--------------------------------------------------------------------
"""

import pytest

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)


CONTENT = """
"Objects"
{
    "{AAA}"
    {
        "Name" = "8:Primeiro.dll"
        "SourcePath" = "8:Primeiro.dll"
        "Folder" = "8:_AAA"
    }

    "{BBB}"
    {
        "AssemblyAsmDisplayName" = "8:Segundo"
        "ScatterAssemblies"
        {
            "_CCC"
            {
                "Name" = "8:Segundo.dll"
                "Attributes" = "3:512"
            }
        }
        "SourcePath" = "8:Segundo.dll"
        "Folder" = "8:_BBB"
    }
}
"""


def test_deve_localizar_bloco_da_dll():
    """
    Deve localizar o bloco estrutural correto da DLL.
    """

    parser = VdprojBlockParser()

    result = parser.find_file_block(
        content=CONTENT,
        file_name="Segundo.dll",
    )

    assert (
        '"Name" = "8:Segundo.dll"'
        in result.content
    )

    assert (
        '"SourcePath" = "8:Segundo.dll"'
        in result.content
    )

    assert (
        '"Folder" = "8:_BBB"'
        in result.content
    )


def test_nao_deve_retornar_somente_scatter_assembly():
    """
    Deve retornar o bloco externo do arquivo,
    e não somente o bloco de ScatterAssemblies.
    """

    parser = VdprojBlockParser()

    result = parser.find_file_block(
        content=CONTENT,
        file_name="Segundo.dll",
    )

    assert (
        '"AssemblyAsmDisplayName"'
        in result.content
    )

    assert (
        '"ScatterAssemblies"'
        in result.content
    )

    assert (
        '"Folder" = "8:_BBB"'
        in result.content
    )


def test_deve_rejeitar_arquivo_inexistente():
    """
    Deve informar quando o arquivo não existe.
    """

    parser = VdprojBlockParser()

    with pytest.raises(
        ValueError,
        match="Arquivo não encontrado",
    ):
        parser.find_file_block(
            content=CONTENT,
            file_name="NaoExiste.dll",
        )