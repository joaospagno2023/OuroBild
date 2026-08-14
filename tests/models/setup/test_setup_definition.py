"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_definition.py
Descrição : Testes do SetupDefinition.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_definition import (
    SetupDefinition,
)


def test_deve_criar_setup_definition():
    """
    Deve criar corretamente uma definição de Setup.
    """

    definition = SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Produto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=Path(
            r"C:\Projetos\Teste\OuroNet.sln",
        ),
        setup_project_path=Path(
            r"C:\Projetos\Teste\Setup\Teste.vdproj",
        ),
        output_msi=Path(
            r"C:\Installers\Teste.msi",
        ),
    )

    assert definition.project_id == (
        "teste"
    )

    assert definition.name == (
        "Projeto Teste"
    )

    assert definition.product_name == (
        "Produto Teste"
    )

    assert definition.manufacturer == (
        "Custom Software"
    )

    assert definition.version == (
        "1.0.0"
    )

    assert definition.configuration == (
        "Release"
    )

    assert definition.platform == (
        "AnyCPU"
    )

    assert definition.solution_path == (
        Path(
            r"C:\Projetos\Teste\OuroNet.sln",
        )
    )

    assert definition.setup_project_path == (
        Path(
            r"C:\Projetos\Teste\Setup\Teste.vdproj",
        )
    )

    assert definition.output_msi == (
        Path(
            r"C:\Installers\Teste.msi",
        )
    )


def test_deve_aceitar_caminhos_como_string():
    """
    O Pydantic deve converter strings em Path.
    """

    definition = SetupDefinition(
        project_id="teste",
        name="Projeto Teste",
        product_name="Produto Teste",
        manufacturer="Custom Software",
        version="1.0.0",
        configuration="Release",
        platform="AnyCPU",
        solution_path=(
            r"C:\Projetos\Teste\OuroNet.sln"
        ),
        setup_project_path=(
            r"C:\Projetos\Teste\Setup\Teste.vdproj"
        ),
        output_msi=(
            r"C:\Installers\Teste.msi"
        ),
    )

    assert isinstance(
        definition.solution_path,
        Path,
    )

    assert isinstance(
        definition.setup_project_path,
        Path,
    )

    assert isinstance(
        definition.output_msi,
        Path,
    )