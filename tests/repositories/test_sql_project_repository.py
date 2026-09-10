"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_sql_project_repository.py
Descrição : Testes do repositório de projetos utilizando SQL Server.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

import pytest

from app.database.models.project_model import ProjectModel
from app.models.build.compilation_engine import CompilationEngine
from app.models.build.compilation_target import CompilationTarget
from app.models.project.project_type import ProjectType
from app.repositories.sql_project_repository import (
    SqlProjectRepository,
)


def create_project_model() -> ProjectModel:
    """
    Cria um ProjectModel para utilização nos testes.
    """

    return ProjectModel(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",
        type=ProjectType.CLIENT.value,
        solution_path=None,
        project_path=(
            r"C:\Projetos\Projeto\Projeto.csproj"
        ),
        compilation_target=(
            CompilationTarget.PROJECT.value
        ),
        compilation_engine=(
            CompilationEngine.MSBUILD.value
        ),
        publish_path=(
            r"C:\Projetos\Projeto\bin\Release"
        ),
        publish_profile=None,
        aip_path=(
            r"C:\Projetos\Projeto\Setup\Projeto.aip"
        ),
        visualstudio_setup_path=None,
        output_msi=(
            r"C:\Setups\Projeto.Setup.msi"
        ),
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def create_repository() -> tuple[
    SqlProjectRepository,
    MagicMock,
    MagicMock,
]:
    """
    Cria o repositório e os mocks necessários.
    """

    database_connection = MagicMock()
    session = MagicMock()

    database_connection.create_session.return_value.__enter__.return_value = (
        session
    )

    repository = SqlProjectRepository(
        database_connection=database_connection,
    )

    return (
        repository,
        database_connection,
        session,
    )


def test_deve_rejeitar_database_connection_nulo() -> None:
    """
    Deve rejeitar DatabaseConnection não informado.
    """

    with pytest.raises(
        ValueError,
        match="DatabaseConnection não foi informado.",
    ):
        SqlProjectRepository(
            database_connection=None,
        )


def test_get_all_deve_retornar_projetos() -> None:
    """
    Deve retornar todos os projetos do banco.
    """

    repository, database_connection, session = (
        create_repository()
    )

    project_model = create_project_model()

    session.scalars.return_value.all.return_value = [
        project_model,
    ]

    result = repository.get_all()

    assert len(result) == 1

    project = result[0]

    assert project.id == "teste"
    assert project.name == "Projeto Teste"
    assert project.description == (
        "Projeto utilizado nos testes."
    )
    assert project.type == ProjectType.CLIENT
    assert project.project_path == (
        r"C:\Projetos\Projeto\Projeto.csproj"
    )
    assert project.compilation_target == (
        CompilationTarget.PROJECT
    )
    assert project.compilation_engine == (
        CompilationEngine.MSBUILD
    )
    assert project.publish_profile is None
    assert project.visualstudio_setup_path is None
    assert project.enabled is True

    database_connection.create_session.assert_called_once()


def test_get_by_id_deve_retornar_projeto() -> None:
    """
    Deve retornar um projeto pelo identificador.
    """

    repository, database_connection, session = (
        create_repository()
    )

    project_model = create_project_model()

    session.scalars.return_value.first.return_value = (
        project_model
    )

    result = repository.get_by_id("teste")

    assert result is not None
    assert result.id == "teste"
    assert result.name == "Projeto Teste"
    assert result.type == ProjectType.CLIENT
    assert result.compilation_target == (
        CompilationTarget.PROJECT
    )
    assert result.compilation_engine == (
        CompilationEngine.MSBUILD
    )
    assert result.enabled is True

    database_connection.create_session.assert_called_once()


def test_get_by_id_deve_retornar_none_quando_nao_encontrar() -> None:
    """
    Deve retornar None quando o projeto não existir.
    """

    repository, _, session = create_repository()

    session.scalars.return_value.first.return_value = None

    result = repository.get_by_id("inexistente")

    assert result is None


def test_get_by_id_deve_rejeitar_id_vazio() -> None:
    """
    Deve rejeitar identificador vazio.
    """

    repository, _, _ = create_repository()

    with pytest.raises(
        ValueError,
        match="ProjectId não foi informado.",
    ):
        repository.get_by_id("")