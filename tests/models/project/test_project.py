"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project.py
Descrição : Testes do modelo Project.
--------------------------------------------------------------------
"""

from app.models.project.project import (
    Project,
)

from app.models.project.project_type import (
    ProjectType,
)


def create_project(
    project_type: str,
) -> Project:
    """
    Cria um projeto mínimo válido para os testes.
    """

    return Project(
        id="teste",
        name="Projeto Teste",
        description="Projeto utilizado nos testes.",
        type=project_type,
        project_path=(
            r"02-Source\Projeto\Projeto.csproj"
        ),
        compilation_target="solution",
        compilation_engine="msbuild",
        publish_path=(
            r"Publish\Projeto"
        ),
        aip_path=(
            r"Setup\Projeto.aip"
        ),
        output_msi="Projeto.msi",
        network_path=(
            r"\\Servidor\Builds"
        ),
        configuration="Release",
        platform="AnyCPU",
        enabled=True,
    )


def test_deve_criar_projeto_com_tipo_client():
    """
    Deve criar um projeto do tipo Client.
    """

    project = create_project(
        "client",
    )

    assert project.type == (
        ProjectType.CLIENT
    )


def test_deve_criar_projeto_com_tipo_server():
    """
    Deve criar um projeto do tipo Server.
    """

    project = create_project(
        "server",
    )

    assert project.type == (
        ProjectType.SERVER
    )