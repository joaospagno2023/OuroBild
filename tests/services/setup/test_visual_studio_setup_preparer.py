from pathlib import Path

import pytest

from app.services.setup.visual_studio_setup_preparer import (
    VisualStudioSetupPreparer,
)


def test_deve_rejeitar_solution_none(
    tmp_path: Path,
):
    """
    Deve rejeitar SolutionPath não informado.
    """

    preparer = VisualStudioSetupPreparer()

    with pytest.raises(
        ValueError,
        match="SolutionPath não foi informado.",
    ):
        preparer.prepare(
            solution_path=None,
            original_setup_project_path=(
                tmp_path / "original.vdproj"
            ),
            prepared_setup_project_path=(
                tmp_path / "prepared.vdproj"
            ),
            workspace_root=(
                tmp_path / "workspace"
            ),
        )


def test_deve_criar_solution_preparada(
    tmp_path: Path,
):
    """
    Deve criar uma cópia da Solution apontando
    para o VDPROJ preparado.
    """

    solution_path = (
        tmp_path
        / "OuroNet 10.4.8.sln"
    )

    original_setup = (
        tmp_path
        / "04-Setup"
        / "Teste"
        / "Teste.vdproj"
    )

    prepared_setup = (
        tmp_path
        / "workspace"
        / "Teste.vdproj"
    )

    workspace_root = (
        tmp_path
        / "solution_workspace"
    )

    #
    # Diretórios
    #

    original_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    prepared_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # Arquivos Setup
    #

    original_setup.write_text(
        "ORIGINAL",
        encoding="utf-8",
    )

    prepared_setup.write_text(
        "PREPARADO",
        encoding="utf-8",
    )

    #
    # Solution
    #

    solution_content = (
        'Microsoft Visual Studio Solution File, '
        'Format Version 12.00\n'

        'Project("{54435603-DBB4-11D2-8724-00A0C9A8B90C}") = '
        '"Teste", '
        '"04-Setup\\Teste\\Teste.vdproj", '
        '"{EF4F3CA0-8FAB-47D3-AEC8-050026D9E848}"\n'

        'EndProject\n'
    )

    solution_path.write_text(
        solution_content,
        encoding="utf-8",
    )

    #
    # Preparer
    #

    preparer = (
        VisualStudioSetupPreparer()
    )

    #
    # Execute
    #

    result = (
        preparer.prepare(
            solution_path=(
                solution_path
            ),
            original_setup_project_path=(
                original_setup
            ),
            prepared_setup_project_path=(
                prepared_setup
            ),
            workspace_root=(
                workspace_root
            ),
        )
    )

    #
    # Assertions
    #

    assert result.exists()

    assert result != solution_path

    prepared_content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    #
    # A Solution preparada deve
    # apontar para o VDPROJ preparado.
    #
    # A referência é relativa à
    # Solution temporária.
    #

    expected_reference = (
        "workspace\\Teste.vdproj"
    )

    assert (
        expected_reference
        in prepared_content
    )

    #
    # A referência original não
    # deve permanecer na Solution
    # preparada.
    #

    assert (
        "04-Setup\\Teste\\Teste.vdproj"
        not in prepared_content
    )

    #
    # A Solution original deve
    # continuar intacta.
    #

    original_content = (
        solution_path.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "04-Setup\\Teste\\Teste.vdproj"
        in original_content
    )


def test_nao_deve_alterar_solution_original(
    tmp_path: Path,
):
    """
    Deve garantir que a Solution original
    nunca seja modificada.
    """

    solution_path = (
        tmp_path
        / "Projeto.sln"
    )

    original_setup = (
        tmp_path
        / "Setup"
        / "Teste.vdproj"
    )

    prepared_setup = (
        tmp_path
        / "prepared"
        / "Teste.vdproj"
    )

    workspace_root = (
        tmp_path
        / "workspace"
    )

    #
    # Diretórios
    #

    original_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    prepared_setup.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    #
    # Arquivos
    #

    original_setup.write_text(
        "ORIGINAL",
        encoding="utf-8",
    )

    prepared_setup.write_text(
        "PREPARADO",
        encoding="utf-8",
    )

    #
    # Referência original
    #

    original_reference = (
        "Setup\\Teste.vdproj"
    )

    #
    # Solution original
    #

    solution_path.write_text(
        'Project("{54435603-DBB4-11D2-8724-00A0C9A8B90C}") = '
        '"Teste", '
        f'"{original_reference}", '
        '"{EF4F3CA0-8FAB-47D3-AEC8-050026D9E848}"\n'
        "EndProject\n",
        encoding="utf-8",
    )

    #
    # Hash/conteúdo original
    #

    original_content = (
        solution_path.read_bytes()
    )

    #
    # Preparer
    #

    preparer = (
        VisualStudioSetupPreparer()
    )

    #
    # Execute
    #

    result = (
        preparer.prepare(
            solution_path=(
                solution_path
            ),
            original_setup_project_path=(
                original_setup
            ),
            prepared_setup_project_path=(
                prepared_setup
            ),
            workspace_root=(
                workspace_root
            ),
        )
    )

    #
    # Solution preparada existe.
    #

    assert result.exists()

    #
    # Solution original continua
    # exatamente igual.
    #

    assert (
        solution_path.read_bytes()
        == original_content
    )

    #
    # A Solution preparada deve
    # apontar para o VDPROJ preparado.
    #

    prepared_content = (
        result.read_text(
            encoding="utf-8",
        )
    )

    assert (
        "prepared\\Teste.vdproj"
        in prepared_content
    )

    #
    # A referência original não
    # deve estar na Solution preparada.
    #

    assert (
        original_reference
        not in prepared_content
    )