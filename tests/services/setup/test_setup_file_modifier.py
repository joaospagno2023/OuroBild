"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_file_modifier.py
Descrição : Testes do SetupFileModifier.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)

from app.services.setup.setup_file_modifier import (
    SetupFileModifier,
)


CONTENT = """
"Objects"
{
    "{AAA}"
    {
        "AssemblyAsmDisplayName" = "8:Primeiro"
        "ScatterAssemblies"
        {
            "_111"
            {
                "Name" = "8:Primeiro.dll"
                "Attributes" = "3:512"
            }
        }
        "SourcePath" = "8:Primeiro.dll"
        "Folder" = "8:_AAA"
    }

    "{BBB}"
    {
        "AssemblyAsmDisplayName" = "8:Segundo"
        "ScatterAssemblies"
        {
            "_222"
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


def create_change(
    name: str,
    source_path: str,
    action: SetupFileAction,
) -> SetupFileSync:
    """
    Cria uma alteração para teste.
    """

    return SetupFileSync(
        name=name,
        source_path=source_path,
        publish_path=Path(
            rf"C:\Publish\{name}"
        ),
        assembly_display_name=None,
        action=action,
    )


def test_deve_atualizar_source_path(
    tmp_path: Path,
):
    """
    Deve alterar somente o SourcePath do arquivo.
    """

    vdproj = (
        tmp_path
        / "Teste.vdproj"
    )

    vdproj.write_text(
        CONTENT,
        encoding="utf-8",
    )

    modifier = (
        SetupFileModifier()
    )

    modifier.apply(
        vdproj_path=vdproj,
        changes=[
            create_change(
                name="Segundo.dll",
                source_path=(
                    r"..\..\Publish\Segundo.dll"
                ),
                action=(
                    SetupFileAction.UPDATE
                ),
            ),
        ],
    )

    content = vdproj.read_text(
        encoding="utf-8",
    )

    assert (
        '"SourcePath" = '
        '"8:..\\..\\Publish\\Segundo.dll"'
        in content
    )

    assert (
        '"SourcePath" = "8:Primeiro.dll"'
        in content
    )

    assert (
        '"Name" = "8:Segundo.dll"'
        in content
    )


def test_deve_remover_bloco_completo(
    tmp_path: Path,
):
    """
    Deve remover o componente completo da DLL.
    """

    vdproj = (
        tmp_path
        / "Teste.vdproj"
    )

    vdproj.write_text(
        CONTENT,
        encoding="utf-8",
    )

    modifier = (
        SetupFileModifier()
    )

    modifier.apply(
        vdproj_path=vdproj,
        changes=[
            create_change(
                name="Segundo.dll",
                source_path=(
                    "Segundo.dll"
                ),
                action=(
                    SetupFileAction.REMOVE
                ),
            ),
        ],
    )

    content = vdproj.read_text(
        encoding="utf-8",
    )

    assert (
        "Segundo.dll"
        not in content
    )

    assert (
        "Primeiro.dll"
        in content
    )

    assert (
        "Primeiro"
        in content
    )


def test_deve_preservar_estrutura_do_outro_componente(
    tmp_path: Path,
):
    """
    Deve preservar integralmente o componente que não foi removido.
    """

    vdproj = (
        tmp_path
        / "Teste.vdproj"
    )

    vdproj.write_text(
        CONTENT,
        encoding="utf-8",
    )

    modifier = (
        SetupFileModifier()
    )

    modifier.apply(
        vdproj_path=vdproj,
        changes=[
            create_change(
                name="Segundo.dll",
                source_path="Segundo.dll",
                action=(
                    SetupFileAction.REMOVE
                ),
            ),
        ],
    )

    content = vdproj.read_text(
        encoding="utf-8",
    )

    assert (
        '"AssemblyAsmDisplayName" = "8:Primeiro"'
        in content
    )

    assert (
        '"Name" = "8:Primeiro.dll"'
        in content
    )

    assert (
        '"SourcePath" = "8:Primeiro.dll"'
        in content
    )

    assert (
        '"Folder" = "8:_AAA"'
        in content
    )


def test_deve_rejeitar_add(
    tmp_path: Path,
):
    """
    Deve rejeitar ADD enquanto a criação de novos blocos
    ainda não estiver implementada.
    """

    vdproj = (
        tmp_path
        / "Teste.vdproj"
    )

    vdproj.write_text(
        CONTENT,
        encoding="utf-8",
    )

    modifier = (
        SetupFileModifier()
    )

    try:
        modifier.apply(
            vdproj_path=vdproj,
            changes=[
                create_change(
                    name="Nova.dll",
                    source_path="Nova.dll",
                    action=(
                        SetupFileAction.ADD
                    ),
                ),
            ],
        )

        assert False

    except NotImplementedError as exc:

        assert (
            "inclusão de novos arquivos"
            in str(exc)
        )