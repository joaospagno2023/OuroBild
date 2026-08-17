"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file_parser.py
Descrição : Testes do SetupFileParser.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.setup_file_parser import (
    SetupFileParser,
)


def test_deve_extrair_dll_do_vdproj(
    tmp_path: Path,
):
    """
    Deve extrair corretamente uma DLL do .vdproj.
    """

    content = """
        {
            "AssemblyRegister" = "3:1"
            "AssemblyIsInGAC" = "11:FALSE"
            "AssemblyAsmDisplayName" = "8:Custom.Framework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=81568928c6d92f5f, processorArchitecture=MSIL"
                "ScatterAssemblies"
                {
                    "_4980BE2A816BF1824B4B6396FD247AAC"
                    {
                        "Name" = "8:Custom.Framework.dll"
                        "Attributes" = "3:512"
                    }
                }
            "SourcePath" = "8:Custom.Framework.dll"
            "TargetName" = "8:"
            "Tag" = "8:"
        }
    """

    parser = SetupFileParser()

    result = parser.parse(
        content=content,
        publish_path=tmp_path,
    )

    assert len(result) == 1

    item = result[0]

    assert item.name == (
        "Custom.Framework.dll"
    )

    assert item.source_path == (
        "Custom.Framework.dll"
    )

    assert item.publish_path == (
        tmp_path
        / "Custom.Framework.dll"
    )

    assert item.assembly_display_name == (
        "Custom.Framework, Version=4.0.0.0, "
        "Culture=neutral, "
        "PublicKeyToken=81568928c6d92f5f, "
        "processorArchitecture=MSIL"
    )


def test_deve_extrair_varias_dlls(
    tmp_path: Path,
):
    """
    Deve extrair várias DLLs do .vdproj.
    """

    content = """
        {
            "AssemblyAsmDisplayName" = "8:Custom.Framework, Version=4.0.0.0"
            "ScatterAssemblies"
            {
                "_AAA"
                {
                    "Name" = "8:Custom.Framework.dll"
                    "Attributes" = "3:512"
                }
            }
            "SourcePath" = "8:Custom.Framework.dll"
            "TargetName" = "8:"
        }

        {
            "AssemblyAsmDisplayName" = "8:OuroNet.Server.Common, Version=10.4.7.0"
            "ScatterAssemblies"
            {
                "_BBB"
                {
                    "Name" = "8:OuroNet.Server.Common.dll"
                    "Attributes" = "3:512"
                }
            }
            "SourcePath" = "8:OuroNet.Server.Common.dll"
            "TargetName" = "8:"
        }
    """

    parser = SetupFileParser()

    result = parser.parse(
        content=content,
        publish_path=tmp_path,
    )

    assert len(result) == 2

    assert result[0].name == (
        "Custom.Framework.dll"
    )

    assert result[1].name == (
        "OuroNet.Server.Common.dll"
    )


def test_deve_retornar_lista_vazia_quando_nao_houver_dll(
    tmp_path: Path,
):
    """
    Deve retornar uma lista vazia quando não houver
    arquivos de Assembly no .vdproj.
    """

    parser = SetupFileParser()

    result = parser.parse(
        content='"ProductName" = "8:Teste"',
        publish_path=tmp_path,
    )

    assert result == []