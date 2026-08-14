"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_visual_studio_setup_definition_loader.py
Descrição : Testes do VisualStudioSetupDefinitionLoader.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.services.setup.visual_studio_setup_definition_loader import (
    VisualStudioSetupDefinitionLoader,
)


VDPROJ_CONTENT = """
"DeployProject"
{
    "VSVersion" = "3:800"
    "ProjectType" = "8:{978C614F-708E-4E1A-B201-565925725DBA}"
    "ProjectName" = "8:OuroNet.Client.App.Setup"

    "Configurations"
    {
        "Debug"
        {
            "DisplayName" = "8:Debug"
            "IsDebugOnly" = "11:TRUE"
            "IsReleaseOnly" = "11:FALSE"
            "OutputFilename" = "8:Debug\\\\OuroNetClientAppSetup.msi"
        }

        "Release"
        {
            "DisplayName" = "8:Release"
            "IsDebugOnly" = "11:FALSE"
            "IsReleaseOnly" = "11:TRUE"
            "OutputFilename" = "8:Release\\\\OuroNetClientAppSetup.msi"
        }
    }

    "Product"
    {
        "ProductName" = "8:OuroNetApp"
        "ProductCode" = "8:{4FCE4DDE-1A7F-4D7D-AB36-2412A30FCC0B}"
        "UpgradeCode" = "8:{EFECFED5-693D-4DA4-8039-F5BD7293C3C5}"
        "ProductVersion" = "8:10.4.800"
        "Manufacturer" = "8:Custom Software"
    }
}
"""


def create_vdproj(
    tmp_path: Path,
) -> Path:
    """
    Cria um .vdproj mínimo para os testes.
    """

    setup_project_path = (
        tmp_path
        / "OuroNet.Client.App.Setup.vdproj"
    )

    setup_project_path.write_text(
        VDPROJ_CONTENT,
        encoding="cp1252",
    )

    return setup_project_path


def create_solution(
    tmp_path: Path,
) -> Path:
    """
    Cria uma solução mínima para os testes.
    """

    solution_path = (
        tmp_path
        / "OuroNet.sln"
    )

    solution_path.write_text(
        "",
        encoding="utf-8",
    )

    return solution_path


def test_deve_carregar_setup_definition(
    tmp_path: Path,
):
    """
    Deve carregar corretamente a definição
    do Setup a partir do .vdproj.
    """

    setup_project_path = create_vdproj(
        tmp_path,
    )

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    result = loader.load(
        setup_project_path=setup_project_path,
        solution_path=solution_path,
        configuration="Release",
        platform="AnyCPU",
    )

    assert isinstance(
        result,
        SetupDefinition,
    )

    assert result.project_id == (
        "OuroNet.Client.App.Setup"
    )

    assert result.name == (
        "OuroNet.Client.App.Setup"
    )

    assert result.product_name == (
        "OuroNetApp"
    )

    assert result.manufacturer == (
        "Custom Software"
    )

    assert result.version == (
        "10.4.800"
    )

    assert result.configuration == (
        "Release"
    )

    assert result.platform == (
        "AnyCPU"
    )

    assert result.solution_path == (
        solution_path
    )

    assert result.setup_project_path == (
        setup_project_path
    )


def test_deve_resolver_output_msi_release(
    tmp_path: Path,
):
    """
    Deve resolver o MSI da configuração Release.
    """

    setup_project_path = create_vdproj(
        tmp_path,
    )

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    result = loader.load(
        setup_project_path=setup_project_path,
        solution_path=solution_path,
        configuration="Release",
    )

    assert result.output_msi == (
        tmp_path
        / "Release"
        / "OuroNetClientAppSetup.msi"
    )


def test_deve_resolver_output_msi_debug(
    tmp_path: Path,
):
    """
    Deve resolver o MSI da configuração Debug.
    """

    setup_project_path = create_vdproj(
        tmp_path,
    )

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    result = loader.load(
        setup_project_path=setup_project_path,
        solution_path=solution_path,
        configuration="Debug",
    )

    assert result.output_msi == (
        tmp_path
        / "Debug"
        / "OuroNetClientAppSetup.msi"
    )


def test_deve_rejeitar_projeto_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar um projeto inexistente.
    """

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    with pytest.raises(
        FileNotFoundError,
        match="projeto de Setup não foi encontrado",
    ):
        loader.load(
            setup_project_path=(
                tmp_path
                / "Inexistente.vdproj"
            ),
            solution_path=solution_path,
            configuration="Release",
        )


def test_deve_rejeitar_solucao_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar uma solução inexistente.
    """

    setup_project_path = create_vdproj(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    with pytest.raises(
        FileNotFoundError,
        match="solução do Setup não foi encontrada",
    ):
        loader.load(
            setup_project_path=setup_project_path,
            solution_path=(
                tmp_path
                / "Inexistente.sln"
            ),
            configuration="Release",
        )


def test_deve_rejeitar_configuracao_inexistente(
    tmp_path: Path,
):
    """
    Deve rejeitar uma configuração que não
    existe no .vdproj.
    """

    setup_project_path = create_vdproj(
        tmp_path,
    )

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="configuração 'Production' não foi encontrada",
    ):
        loader.load(
            setup_project_path=setup_project_path,
            solution_path=solution_path,
            configuration="Production",
        )


def test_deve_rejeitar_projeto_sem_product_name(
    tmp_path: Path,
):
    """
    Deve rejeitar um .vdproj sem ProductName.
    """

    content = VDPROJ_CONTENT.replace(
        '"ProductName" = "8:OuroNetApp"',
        "",
    )

    setup_project_path = (
        tmp_path
        / "Teste.vdproj"
    )

    setup_project_path.write_text(
        content,
        encoding="cp1252",
    )

    solution_path = create_solution(
        tmp_path,
    )

    loader = (
        VisualStudioSetupDefinitionLoader()
    )

    with pytest.raises(
        ValueError,
        match="ProductName.*não foi encontrado",
    ):
        loader.load(
            setup_project_path=setup_project_path,
            solution_path=solution_path,
            configuration="Release",
        )