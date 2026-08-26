"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_temporary_solution_service.py
Descrição : Testes do serviço de criação de Solution temporária.
--------------------------------------------------------------------
"""

from pathlib import Path

import pytest

from app.services.setup.temporary_solution_service import (
    TemporarySolutionService,
)


def create_solution(
    tmp_path: Path,
) -> tuple[Path, Path]:
    """
    Cria uma Solution de teste e o projeto Setup original.
    """

    solution_root = (
        tmp_path
        / "OuroNet"
    )

    setup_root = (
        solution_root
        / "04-Setup"
        / "OuroNet.Client.WinServiceLinkPagamento.Setup"
    )

    setup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_project = (
        setup_root
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
    )

    setup_project.write_text(
        '"Test" = "8:Setup"',
        encoding="utf-8",
    )

    solution = (
        solution_root
        / "OuroNet 10.4.8.sln"
    )

    solution.write_text(
        """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17

Project("{54435603-DBB4-11D2-8724-00A0C9A8B90C}") = "OuroNet.Client.WinServiceLinkPagamento.Setup", "04-Setup\\OuroNet.Client.WinServiceLinkPagamento.Setup\\OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj", "{EF4F3CA0-8FAB-47D3-AEC8-050026D9E848}"
EndProject

Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "OuroNet.Client.WinService.LinkPagamento", "02-Source\\01-Client\\OuroNet.Client.WinService.LinkPagamento\\OuroNet.Client.WinService.LinkPagamento.csproj", "{CF9D268B-5FCB-4BE6-8E49-F1B0E17EC20D}"
EndProject

Global
EndGlobal
""".strip(),
        encoding="utf-8",
    )

    return solution, setup_project


def test_deve_criar_solution_temporaria(
    tmp_path: Path,
) -> None:
    """
    Deve criar uma cópia temporária da Solution.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    result = service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    assert result.exists()

    assert result.name == (
        "OuroNet 10.4.8.OuroBuild.sln"
    )

    assert result.parent == (
        publish_path
    )


def test_nao_deve_alterar_solution_original(
    tmp_path: Path,
) -> None:
    """
    A Solution original deve permanecer intacta.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    original_content = (
        solution.read_text(
            encoding="utf-8",
        )
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    assert (
        solution.read_text(
            encoding="utf-8",
        )
        == original_content
    )


def test_deve_apontar_setup_para_arquivo_temporario(
    tmp_path: Path,
) -> None:
    """
    A Solution temporária deve apontar para o
    VDPROJ temporário.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    result = service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
        in content
    )

    assert (
        "OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
        not in content
    )


def test_deve_manter_projetos_originais(
    tmp_path: Path,
) -> None:
    """
    Os demais projetos devem continuar sendo referenciados.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    result = service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "OuroNet.Client.WinService.LinkPagamento.csproj"
        in content
    )

    assert (
        "{CF9D268B-5FCB-4BE6-8E49-F1B0E17EC20D}"
        in content
    )


def test_deve_manter_guid_do_setup(
    tmp_path: Path,
) -> None:
    """
    O GUID do projeto Setup deve permanecer o mesmo.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    result = service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "{EF4F3CA0-8FAB-47D3-AEC8-050026D9E848}"
        in content
    )


def test_deve_falhar_se_solution_nao_existir(
    tmp_path: Path,
) -> None:
    """
    Deve informar erro quando a Solution não existir.
    """

    service = (
        TemporarySolutionService()
    )

    solution = (
        tmp_path
        / "inexistente.sln"
    )

    setup = (
        tmp_path
        / "Setup.vdproj"
    )

    setup.write_text(
        "setup",
        encoding="utf-8",
    )

    temporary_setup = (
        tmp_path
        / "Setup.OuroBuild.vdproj"
    )

    temporary_setup.write_text(
        "setup",
        encoding="utf-8",
    )

    with pytest.raises(
        FileNotFoundError,
        match="Solution original não encontrada",
    ):
        service.create(
            solution_path=solution,
            publish_path=(
                tmp_path
                / ".ourobuild"
            ),
            original_setup_project_path=setup,
            temporary_setup_project_path=temporary_setup,
        )


def test_deve_falhar_se_setup_temporario_nao_existir(
    tmp_path: Path,
) -> None:
    """
    Deve informar erro quando o VDPROJ temporário
    não existir.
    """

    solution, setup_project = create_solution(
        tmp_path,
    )

    service = (
        TemporarySolutionService()
    )

    temporary_setup = (
        tmp_path
        / ".ourobuild"
        / "Setup.OuroBuild.vdproj"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Projeto Setup temporário não encontrado",
    ):
        service.create(
            solution_path=solution,
            publish_path=(
                tmp_path
                / ".ourobuild"
            ),
            original_setup_project_path=setup_project,
            temporary_setup_project_path=temporary_setup,
        )

def create_solution_with_scc_binding(
    tmp_path: Path,
) -> tuple[Path, Path]:
    """
    Cria uma Solution de teste contendo um binding de
    source control (GlobalSection(SourceCodeControl))
    apontando para o provider fictício "SAK".
    """

    solution_root = (
        tmp_path
        / "OuroNet"
    )

    setup_root = (
        solution_root
        / "04-Setup"
        / "OuroNet.Client.WinServiceLinkPagamento.Setup"
    )

    setup_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    setup_project = (
        setup_root
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj"
    )

    setup_project.write_text(
        '"Test" = "8:Setup"',
        encoding="utf-8",
    )

    solution = (
        solution_root
        / "OuroNet 10.4.8.sln"
    )

    solution.write_text(
        (
            "Microsoft Visual Studio Solution File, Format Version 12.00\r\n"
            "# Visual Studio Version 17\r\n"
            "\r\n"
            'Project("{54435603-DBB4-11D2-8724-00A0C9A8B90C}") = '
            '"OuroNet.Client.WinServiceLinkPagamento.Setup", '
            '"04-Setup\\OuroNet.Client.WinServiceLinkPagamento.Setup\\'
            'OuroNet.Client.WinServiceLinkPagamento.Setup.vdproj", '
            '"{EF4F3CA0-8FAB-47D3-AEC8-050026D9E848}"\r\n'
            "EndProject\r\n"
            "\r\n"
            'Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = '
            '"OuroNet.Client.WinService.LinkPagamento", '
            '"02-Source\\01-Client\\OuroNet.Client.WinService.LinkPagamento\\'
            'OuroNet.Client.WinService.LinkPagamento.csproj", '
            '"{CF9D268B-5FCB-4BE6-8E49-F1B0E17EC20D}"\r\n'
            "EndProject\r\n"
            "\r\n"
            "Global\r\n"
            "\tGlobalSection(SourceCodeControl) = preSolution\r\n"
            "\t\tSccNumberOfProjects = 2\r\n"
            "\t\tSccEnterpriseProvider = SAK\r\n"
            "\t\tSccProjectName0 = SAK\r\n"
            "\t\tSccLocalPath0 = SAK\r\n"
            "\t\tSccProvider0 = SAK\r\n"
            "\t\tSccProjectUniqueName1 = 04-Setup\\\\OuroNet.Client.Win\r\n"
            "\t\tSccProjectName1 = SAK\r\n"
            "\t\tSccLocalPath1 = SAK\r\n"
            "\t\tSccProvider1 = SAK\r\n"
            "\tEndGlobalSection\r\n"
            "\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\r\n"
            "\t\tRelease|Any CPU = Release|Any CPU\r\n"
            "\tEndGlobalSection\r\n"
            "EndGlobal\r\n"
        ),
        encoding="utf-8",
    )

    return solution, setup_project


def test_deve_remover_bindings_de_source_control(
    tmp_path: Path,
) -> None:
    """
    A Solution temporária não deve conter bindings de
    source control ("Scc*"), inclusive o GlobalSection
    (SourceCodeControl) inteiro.

    Sem essa limpeza, o devenv.com recusa a geração do
    Setup com o erro:

        "Could not find the 'SAK' source control provider
         set by the 'SccProvider' property."
    """

    solution, setup_project = (
        create_solution_with_scc_binding(
            tmp_path,
        )
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    result = service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    temporary_content = result.read_text(
        encoding="utf-8",
    )

    assert "SAK" not in temporary_content

    assert "Scc" not in temporary_content

    assert (
        "GlobalSection(SourceCodeControl)"
        not in temporary_content
    )

    #
    # As demais seções da Solution devem
    # permanecer intactas.
    #

    assert (
        "GlobalSection(SolutionConfigurationPlatforms)"
        in temporary_content
    )

    assert "EndGlobal" in temporary_content


def test_nao_deve_alterar_bindings_scc_da_solution_original(
    tmp_path: Path,
) -> None:
    """
    A Solution original deve permanecer intacta,
    inclusive os bindings de source control.
    """

    solution, setup_project = (
        create_solution_with_scc_binding(
            tmp_path,
        )
    )

    original_content = solution.read_text(
        encoding="utf-8",
    )

    publish_path = (
        tmp_path
        / ".ourobuild"
    )

    temporary_setup = (
        publish_path
        / "OuroNet.Client.WinServiceLinkPagamento.Setup.OuroBuild.vdproj"
    )

    temporary_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_setup.write_text(
        '"Test" = "8:Setup temporario"',
        encoding="utf-8",
    )

    service = (
        TemporarySolutionService()
    )

    service.create(
        solution_path=solution,
        publish_path=publish_path,
        original_setup_project_path=setup_project,
        temporary_setup_project_path=temporary_setup,
    )

    assert solution.read_text(
        encoding="utf-8",
    ) == original_content

    assert "SAK" in original_content