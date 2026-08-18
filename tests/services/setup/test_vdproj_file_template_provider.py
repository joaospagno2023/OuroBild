"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_vdproj_file_template_provider.py
Descrição : Testes do VdprojFileTemplateProvider.
--------------------------------------------------------------------
"""

import pytest

from app.services.setup.vdproj_block_parser import (
    VdprojBlockParser,
)

from app.services.setup.vdproj_file_template_provider import (
    VdprojFileTemplateProvider,
)


CONTENT = """
"File"
{
    "{AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA}:_11111111111111111111111111111111"
    {
        "AssemblyRegister" = "3:1"
        "AssemblyIsInGAC" = "11:FALSE"
        "AssemblyAsmDisplayName" = "8:Primeiro, Version=1.0.0.0"

        "ScatterAssemblies"
        {
            "_111111"
            {
                "Name" = "8:Primeiro.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Primeiro.dll"
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
        "AssemblyAsmDisplayName" = "8:Segundo, Version=2.0.0.0"

        "ScatterAssemblies"
        {
            "_222222"
            {
                "Name" = "8:Segundo.dll"
                "Attributes" = "3:512"
            }
        }

        "SourcePath" = "8:Segundo.dll"
        "TargetName" = "8:"
        "Tag" = "8:"
        "Folder" = "8:_BBBBBB"
        "Condition" = "8:"
        "Transitive" = "11:FALSE"
        "Vital" = "11:TRUE"
    }
}
"""


def create_provider():
    """
    Cria o Provider utilizando o parser real.
    """

    parser = (
        VdprojBlockParser()
    )

    return VdprojFileTemplateProvider(
        parser=parser,
    )


def test_deve_obter_template_do_arquivo():
    """
    Deve retornar o bloco completo do arquivo.
    """

    provider = create_provider()

    result = provider.get_template(
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
        '"AssemblyAsmDisplayName"'
        in result.content
    )

    assert (
        '"Folder" = "8:_BBBBBB"'
        in result.content
    )


def test_deve_retornar_posicoes_do_bloco():
    """
    Deve preservar as posições identificadas pelo parser.
    """

    provider = create_provider()

    result = provider.get_template(
        content=CONTENT,
        file_name="Segundo.dll",
    )

    assert result.start >= 0

    assert result.end > result.start

    assert (
        CONTENT[result.start:result.end]
        == result.content
    )


def test_deve_rejeitar_conteudo_none():
    """
    Deve rejeitar conteúdo não informado.
    """

    provider = create_provider()

    with pytest.raises(
        ValueError,
        match="Conteúdo do .vdproj não foi informado.",
    ):
        provider.get_template(
            content=None,
            file_name="Segundo.dll",
        )


def test_deve_rejeitar_nome_nao_informado():
    """
    Deve rejeitar nome de arquivo não informado.
    """

    provider = create_provider()

    with pytest.raises(
        ValueError,
        match="Nome do arquivo não foi informado.",
    ):
        provider.get_template(
            content=CONTENT,
            file_name="",
        )


def test_deve_propagar_erro_do_parser():
    """
    Deve propagar o erro quando o arquivo não existir.
    """

    provider = create_provider()

    with pytest.raises(
        ValueError,
        match="Arquivo não encontrado no .vdproj",
    ):
        provider.get_template(
            content=CONTENT,
            file_name="NaoExiste.dll",
        )