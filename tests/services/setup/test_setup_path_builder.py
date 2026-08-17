"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_path_builder.py
Descrição : Testes do SetupPathBuilder.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.services.setup.setup_path_builder import (
    SetupPathBuilder,
)


def test_deve_calcular_source_path_relativo():
    """
    Deve calcular corretamente o caminho relativo
    entre o .vdproj e o publish_path.
    """

    vdproj_path = Path(
        r"C:\Projetos\OuroNet\04-Setup\Meu.Setup\Meu.Setup.vdproj"
    )

    publish_path = Path(
        r"C:\Projetos\OuroNet\02-Source\Projeto\bin\Release"
    )

    builder = SetupPathBuilder()

    result = builder.build_source_path(
        vdproj_path=vdproj_path,
        publish_path=publish_path,
        file_name="MinhaAplicacao.dll",
    )

    assert result == (
        r"..\..\02-Source\Projeto\bin\Release"
        r"\MinhaAplicacao.dll"
    )


def test_deve_rejeitar_nome_vazio():
    """
    Deve rejeitar nome de arquivo vazio.
    """

    builder = SetupPathBuilder()

    try:
        builder.build_source_path(
            vdproj_path=Path(
                r"C:\Setup\Meu.Setup.vdproj"
            ),
            publish_path=Path(
                r"C:\Publish"
            ),
            file_name="",
        )

        assert False

    except ValueError as exc:

        assert str(exc) == (
            "Nome do arquivo não foi informado."
        )